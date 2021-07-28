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

import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;
import java.io.InputStream;


/**
 *  This class is used to manage and validate xml file using an schema    
 *  @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 *  @version 1.3
 */
public class JAXPValidator {
  private ErrorHandler handler;
  private static final String JAXP_SCHEMA_LANGUAGE = "http://java.sun.com/xml/jaxp/properties/schemaLanguage";
  private static final String JAXP_SCHEMA_SOURCE = "http://java.sun.com/xml/jaxp/properties/schemaSource";
  private static final String W3C_XML_SCHEMA = "http://www.w3.org/2001/XMLSchema";

  public JAXPValidator(){
    handler = new SAXErrorHandler();
  }

  public String validator(InputStream is,String SchemaUrl) {
    String s="";

    try {
      DocumentBuilderFactory factory
       = DocumentBuilderFactory.newInstance();
      // Always turn on namespace awareness
      factory.setNamespaceAware(true);
      // Turn on validation
      factory.setValidating(true);
      factory.setAttribute(JAXP_SCHEMA_LANGUAGE,W3C_XML_SCHEMA);
      factory.setAttribute(JAXP_SCHEMA_SOURCE,SchemaUrl);
      DocumentBuilder parser = factory.newDocumentBuilder();

      // SAXErrorHandler
      parser.setErrorHandler(handler);

      parser.parse(is);

      if (((SAXErrorHandler)handler).isValid()) {
        s="Policy document is valid.\n";
      }
      else {
        // If the document isn't well-formed, an exception has
        // already been thrown and this has been skipped.
        s="Policy document is well-formed.\n";
      }

    }
    catch (SAXException e) {
      s="Policy document is not well-formed.\n";
    }
    catch (IOException e) {
      e.printStackTrace();
    }
    catch (FactoryConfigurationError e) {
      s="Could not locate a factory class\n";
    }
    catch (ParserConfigurationException e) {
      s="Could not locate a JAXP parser\n";
    }

    s+=((SAXErrorHandler)handler).getErrores();
    return s;
  }


  public String validator(String XmlDocumentUrl,String SchemaUrl) {
    String s="";

    try {
      DocumentBuilderFactory factory
       = DocumentBuilderFactory.newInstance();
      // Always turn on namespace awareness
      factory.setNamespaceAware(true);
      // Turn on validation
      factory.setValidating(true);
      factory.setAttribute(JAXP_SCHEMA_LANGUAGE,W3C_XML_SCHEMA);
      factory.setAttribute(JAXP_SCHEMA_SOURCE,SchemaUrl);
      DocumentBuilder parser = factory.newDocumentBuilder();

      // SAXErrorHandler
      parser.setErrorHandler(handler);

      parser.parse(XmlDocumentUrl);
      if (((SAXErrorHandler)handler).isValid()) {
        s=XmlDocumentUrl + " is valid.\n";
      }
      else {
        // If the document isn't well-formed, an exception has
        // already been thrown and this has been skipped.
        s=XmlDocumentUrl + " is well-formed.\n";
      }

    }
    catch (SAXException e) {
      s=XmlDocumentUrl + " is not well-formed.\n";
    }
    catch (IOException e) {
      s="Due to an IOException, the parser could not check " + XmlDocumentUrl +"\n";
    }
    catch (FactoryConfigurationError e) {
      s="Could not locate a factory class\n";
    }
    catch (ParserConfigurationException e) {
      s="Could not locate a JAXP parser\n";
    }

    s+=((SAXErrorHandler)handler).getErrores();
    return s;
  }

}
