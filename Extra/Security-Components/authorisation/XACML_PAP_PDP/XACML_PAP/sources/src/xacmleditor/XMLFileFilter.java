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

import javax.swing.filechooser.FileFilter;
import java.io.File;


/* *********************************************************
 * Name: XMLFileFilter
 *
 * Description: *//** A filter for .XML files in a
 * JFileChooser.
 *
 * @author not attributable
 * @version 1.3
 ***********************************************************/
public class XMLFileFilter
    extends FileFilter {

  private String ext;

  public XMLFileFilter(String ext) {
    this.ext=ext;
  }

  /**
   * Tests whether or not the specified abstract pathname should be included in
   * a pathname list.
   *
   * @param f The abstract pathname to be tested
   * @return <code>true</code> if and only if <code>pathname</code> should be
   *   included
   * todo Implement this java.io.FileFilter method
   */
  public boolean accept(File f) {
    if (f.isDirectory()) {
      return true;
    }
    String nombre = f.getName();
    String extension = null;
    if (nombre.length() > 4) {
      extension = nombre.substring(nombre.length() - 4, nombre.length());
    }
    if (extension != null) {
      if (extension.equalsIgnoreCase("."+ext)) {
        return true;
      }
      else {
        return false;
      }

    }

    return false;
  }

  public String getDescription() {
    return ext.toUpperCase()+" files (*."+ext.toLowerCase()+")";
  }

}
