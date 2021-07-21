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

import org.jdom.input.DOMBuilder;
import org.jdom.output.Format;
import org.jdom.output.XMLOutputter;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreeModel;
import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.*;

/**
 * This class is used to manage the SAX operations.
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 * @version 1.3
 */
public class AnalizadorSAX
    extends DefaultHandler {

  private MiContentHandler contentHandler;
  private SAXErrorHandler errorHandler;

  public AnalizadorSAX() {
    this.contentHandler = new MiContentHandler();
    this.errorHandler = new SAXErrorHandler();
  }

  public TreeModel analizar(String uri) throws IOException, SAXException {

    try {
      SAXParserFactory parserFactory = SAXParserFactory.newInstance();

      SAXParser saxParser = parserFactory.newSAXParser();

      XMLReader parser = saxParser.getXMLReader();
      parser = saxParser.getXMLReader();
      parser.setErrorHandler(errorHandler);
      parser.setContentHandler(contentHandler);
      InputSource in = new InputSource(new FileInputStream(new File(uri)));      
      parser.parse(in);
      if (!contentHandler.getWarnings().equalsIgnoreCase("")) {
        errorHandler.setErrores(contentHandler.getWarnings() +
                                errorHandler.getErrores());
      }
    }
    catch (ParserConfigurationException exception) {
      exception.printStackTrace();
    }
    catch (FactoryConfigurationError exception) {
      exception.printStackTrace();
    }
    return contentHandler.getDatos();
  }

  // JR
  public TreeModel analizarFromString(String toParse) throws IOException, SAXException {

	    try {
	      SAXParserFactory parserFactory = SAXParserFactory.newInstance();

	      SAXParser saxParser = parserFactory.newSAXParser();

	      XMLReader parser = saxParser.getXMLReader();
	      parser = saxParser.getXMLReader();
	      parser.setErrorHandler(errorHandler);
	      parser.setContentHandler(contentHandler);
	      parser.parse(new InputSource(new ByteArrayInputStream(toParse.getBytes())));
	      if (!contentHandler.getWarnings().equalsIgnoreCase("")) {
	        errorHandler.setErrores(contentHandler.getWarnings() +
	                                errorHandler.getErrores());
	      }
	    }
	    catch (ParserConfigurationException exception) {
	      exception.printStackTrace();
	    }
	    catch (FactoryConfigurationError exception) {
	      exception.printStackTrace();
	    }
	    return contentHandler.getDatos();
	  }
  // JREND

  public String getErrorHandler() {
    return errorHandler.getErrores();
  }

  public void procesaSalvar(DefaultMutableTreeNode node, String uri) {
    try {
      Document document = ConversorDOM.convierte(node);
      DOMBuilder builder = new DOMBuilder();
      org.jdom.Document jdomDoc = builder.build(document);

      XMLOutputter outputter = new XMLOutputter(Format.getPrettyFormat());
      File newXML = new File(uri);
      FileOutputStream os = new FileOutputStream(newXML);
      outputter.output(jdomDoc, os);
      os.close();
    }
    catch (IOException ioe) {
// I/O error
      ioe.printStackTrace();
    }

  }

  public void procesaValidar(DefaultMutableTreeNode node, OutputStream os) {
    try {
      Document document = ConversorDOM.convierte(node);
      DOMBuilder builder = new DOMBuilder();
      org.jdom.Document jdomDoc = builder.build(document);

      XMLOutputter outputter = new XMLOutputter(Format.getPrettyFormat());
      outputter.output( jdomDoc, os);
    }
    catch (IOException ioe) {
// I/O error
      ioe.printStackTrace();
    }

  }


} //fin class
