/*
 * Copyright 2005, 2006 Alberto Jiménez Lázaro
 *                      Pablo Galera Morcillo (umu-xacml-editor-admin@dif.um.es)
 *                      Dpto. de Ingeniería de la Información y las Comunicaciones
 *                      (http://www.diic.um.es:8080/diic/index.jsp)
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
package xacmleditor;

import org.xml.sax.Attributes;
import org.xml.sax.ContentHandler;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreeModel;
import java.util.Hashtable;

/**
 * This class implements the SAX ContentHandler Interface and permits manage the xml content
 * when sax processor is visiting the nodes
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 * @version 1.3
 */
public class MiContentHandler
    implements ContentHandler {
  private TreeModel datos;
  private DefaultMutableTreeNode elementoActual;
  int profundidad = 0;
  String elemento;
  private String warnings = "";
  boolean resto=false;

  public void startPrefixMapping(String prefix, String uri) {

  }

  public TreeModel getDatos() {
    return this.datos;
  }

  public void setDocumentLocator(Locator locator) {
  }

  public void startDocument() throws SAXException {
    elementoActual = new DefaultMutableTreeNode(new String("Policy Document"));
  }

  public void endDocument() throws SAXException {
    datos = new DefaultTreeModel(elementoActual);
  }

  public void processingInstruction(String target, String data) throws
      SAXException {
  }

  public void endPrefixMapping(String prefix) {
  }

  public void startElement(String namespaceURI, String localName, String qName,
                           Attributes atts) throws SAXException {

    ElementoXACMLFactory factory = ElementoXACMLFactoryImpl.getInstance();
    Hashtable atributos = new Hashtable();
    for (int i = 0; i < atts.getLength(); i++) {
      atributos.put(atts.getQName(i), atts.getValue(i));
    }
    if(!resto){
           ElementoXACML elem = factory.obtenerElementoXACML(qName, atributos);
           DefaultMutableTreeNode aux = new DefaultMutableTreeNode(elem);
           if (elem instanceof ElementoAttributeValue){
             resto=true;
           }
           elementoActual.add(aux);
           elementoActual = aux;
           profundidad += 1;
           elemento = localName;
    }else{
      ((ElementoXACML)elementoActual.getUserObject()).addContenido("<"+qName+">");
    }
  }

  public void endElement(String namespaceURI, String localName, String qName) throws
      SAXException {
    profundidad -= 1;
    ElementoXACML e = (ElementoXACML)elementoActual.getUserObject();
    if(e instanceof ElementoAttributeValue && e.getTipo().equals(qName)){
      resto = false;
    }else if(resto){
      ((ElementoXACML)elementoActual.getUserObject()).addContenido("</"+qName+">");
    }
    if(!resto){
      if (e == null) {
        DefaultMutableTreeNode aux = elementoActual;
        elementoActual = (DefaultMutableTreeNode) elementoActual.getParent();
        elementoActual.remove(aux);
        // JR Notify AnySubject/AnyResource/AnyAction is no longer in XACML 2.0
        if (qName.equals("AnySubject") || qName.equals("AnyResource") || 
        	qName.equals("AnyAction")) {
        	warnings += "<" + qName + "> has been removed from XACML 2.0\n";
        }
        else {
        	// English
        	// warnings += "<" + qName + "> Label nonrecognized\n";
        	warnings += "<" + qName + "> is not recognized.\n";
        }
        // JREND
      }
      else {
        if (elementoActual.isLeaf()) {
          ( (ElementoXACML) e).setVacio(true);
        }
        elementoActual = (DefaultMutableTreeNode) elementoActual.getParent();
      }
    }
  }

  public void characters(char[] ch, int start, int end) throws SAXException {
    String s = new String(ch, start, end);
    if (elementoActual != null) {
      Object e = elementoActual.getUserObject();
      if (e != null && e instanceof ElementoXACML) {
        s = s.replaceAll("\t", "");
        s = s.trim();
        ( (ElementoXACML) e).addContenido(s);
      }
    }
  }

  public void ignorableWhitespace(char[] ch, int start, int end) throws
      SAXException {
  }

  public void skippedEntity(String name) throws SAXException {
  }

  public String getWarnings() {
    return warnings;
  }

} //fin class
