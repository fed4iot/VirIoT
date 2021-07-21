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

/* ***************************************************************
 * Name: Creditos
 * Description : *//**
 * This class is only a Dialog with information about this project and
 * its authors.
 *
 * @author Alberto Jimenez Lazaro & Pablo Galera Morcillo
 * @version 1.3
 *****************************************************************/
public class Creditos
    extends JDialog {

  JTextArea informacion = new JTextArea();

  public Creditos() {
    try {
      setDefaultCloseOperation(DISPOSE_ON_CLOSE);
      jbInit();
      pack();
    }
    catch (Exception exception) {
      exception.printStackTrace();
    }
  }


  private void jbInit() throws Exception {
    //this.setLayout(new MiLayout());
      this.getContentPane().setLayout(new MiLayout());
    setTitle("Credits");
    informacion.setText(
"UMU-XACML-Editor\n\n"+
"University of Murcia (UMU)\n\n"+
"Authors:\n"+
"    Pablo Galera Morcillo\n"+
"    Alberto Jiménez Lázaro\n\n"+
"Project Coordinators:\n"+
"    Antonio F. Gómez Skarmeta\n"+
"    Gregorio Martínez Pérez\n"+
"    Gabriel López Millán\n\n"+
"Contact E-Mail: umu-xacml-editor-admin@dif.um.es");
    informacion.setEditable(false);
    this.getContentPane().add(new JScrollPane(informacion));
  }

}
