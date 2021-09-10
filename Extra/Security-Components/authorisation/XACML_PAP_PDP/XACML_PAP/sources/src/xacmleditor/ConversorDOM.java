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

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Text;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.util.Collection;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.Map;

/* ***************************************************************
 * Name: ConversorDOM
 * Description : *//**
 * This class is an utility to extract the information of the
 * tree nodes and transform it in a a JDOM XML representation.
 *
 * @author Alberto Jimenez Lazaro & Pablo Galera Morcillo
 * @version 1.3
 *****************************************************************/
public class ConversorDOM {

  public static Document convierte(DefaultMutableTreeNode root) {
    Document ret = null;
    try {

      DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
      DocumentBuilder docBuilder = factory.newDocumentBuilder();

      if (root.getUserObject() instanceof String) {
        String st=(String)root.getUserObject();
        ret=docBuilder.newDocument();
      }
      else {
        return ret;
      }


      Enumeration hijos=root.children();
      while(hijos.hasMoreElements()){
        ret.appendChild(procesaHijo((DefaultMutableTreeNode)hijos.nextElement(),ret));
      }
      return ret;


    }
    catch (ParserConfigurationException pce) {

    }

    return ret;
  }

  private static Element procesaHijo(DefaultMutableTreeNode node,Document doc){
    ElementoXACML elemento=(ElementoXACML) node.getUserObject();
    Element ret=doc.createElement(elemento.getTipo());

    Enumeration hijos=node.children();
    while(hijos.hasMoreElements()){
      ret.appendChild(procesaHijo((DefaultMutableTreeNode)hijos.nextElement(),doc));
    }

    Map atributos=elemento.getAtributos();
    Collection claves=(Collection)atributos.keySet();
    Iterator it=claves.iterator();
    while(it.hasNext()){
      String clave=(String)it.next();
      ret.setAttribute(clave,(String)atributos.get(clave));
    }

    String texto=elemento.getContenido();
    if(texto!=null){
      Text txt=doc.createTextNode(texto);
      ret.appendChild(txt);
    }

    return ret;
  }

}
