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

import javax.swing.*;
import java.awt.*;


/* ****************************************************************
 * Title: Aplicacion.java
 *
 * Description: *//** Main class of the program.
 *
 *
 * @author Alberto Jiménez Lázaro & Pablo Galera Morcillo
 * @version 1.3
 ******************************************************************/
public class Aplicacion {
  boolean packFrame = false;

 /* **************************************************************
   * Name: Aplicacion
   *
   * Description: *//** Construct and show the application.*//*
   *
   * Author: Alberto Jiménez Lázaro & Pablo Galera Morcillo
   *
   * Date: 5/10/2005
   *****************************************************************/
  public Aplicacion() {
    PrincipalPolitica frame = new PrincipalPolitica();
    // Validate frames that have preset sizes
    // Pack frames that have useful preferred size info, e.g. from their layout
    if (packFrame) {
      frame.pack();
    }
    else {
      frame.validate();
    }

    // Center the window
    Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
    Dimension inicioSize = frame.getSize();
    if (inicioSize.height > screenSize.height) {
      inicioSize.height = screenSize.height;
    }
    if (inicioSize.width > screenSize.width) {
      inicioSize.width = screenSize.width;
    }
    frame.setLocation( (screenSize.width - inicioSize.width) / 2,
                      (screenSize.height- inicioSize.height) / 2);
    frame.setVisible(true);

    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  /**
   * Application entry point.
   *
   * @param args String[]
   */
  public static void main(String[] args) {
    SwingUtilities.invokeLater(new Runnable() {
      public void run() {
        try {
            // turn off bold fonts
              UIManager.put("swing.boldMetal", Boolean.FALSE);

              // re-install the Metal Look and Feel
              UIManager.setLookAndFeel(new javax.swing.plaf.metal.MetalLookAndFeel());
            }
        catch (Exception exception) {
          exception.printStackTrace();
        }

        new Aplicacion();
      }
    });
  }

  private void jbInit() throws Exception {
  }
}
