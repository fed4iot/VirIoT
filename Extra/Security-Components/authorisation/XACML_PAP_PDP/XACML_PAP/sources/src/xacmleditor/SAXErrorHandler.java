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
import org.xml.sax.SAXParseException;


/**
 * This class implements the SAX ErrorHandler Interface and manage the
 * posible errors in the SAX process.  
 *
 * @author Alberto Jimenez Lazaro y Pablo Galera Morcillo
 * @version 1.3
 */

public class SAXErrorHandler implements ErrorHandler {

  // Flag to check whether any errors have been spotted.
  private boolean valid = true;
  private String errores="";

  public boolean isValid() {
    return valid;
  }

  public String getErrores(){
    return errores;
  }

  public void setErrores(String err){
    errores=err;
  }

  // If this handler is used to parse more than one document,
  // its initial state needs to be reset between parses.
  public void reset() {
    // Assume document is valid until proven otherwise
    valid = true;
  }

  public void warning(SAXParseException exception) {

    errores+="Warning: " + exception.getMessage()+"\n";
    errores+=" at line " + exception.getLineNumber()
     + ", column " + exception.getColumnNumber()+"\n";
    // Well-formedness is a prerequisite for validity
    valid = false;

  }

  public void error(SAXParseException exception) {

    errores+="Error: " + exception.getMessage()+"\n";
    errores+=" at line " + exception.getLineNumber()
     + ", column " + exception.getColumnNumber()+"\n";
    // Unfortunately there's no good way to distinguish between
    // validity errors and other kinds of non-fatal errors
    valid = false;

  }

  public void fatalError(SAXParseException exception) {

    errores+="Fatal Error: " + exception.getMessage()+"\n";
    errores+=" at line " + exception.getLineNumber()
     + ", column " + exception.getColumnNumber()+"\n";

  }

}
