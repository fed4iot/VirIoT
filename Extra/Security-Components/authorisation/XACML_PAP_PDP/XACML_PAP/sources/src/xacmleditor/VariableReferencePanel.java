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
import javax.swing.tree.DefaultMutableTreeNode;
import java.awt.*;
import java.awt.event.KeyEvent;
import java.util.Map;

/** It's a panel for editing VariableReference elements of the XACML 2.0 standard
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class VariableReferencePanel
    extends ElementPanel {

  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public VariableReferencePanel(DefaultMutableTreeNode n) {
    super(n);
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }
  /* *******************************************************************
	 * Name: inicializate *//** Inicialize the graphics components.
	 *
	 * @exception Exception If the Inicialization of any components fails.
	 *//*
	 *
	 * Author: Alberto Jiménez Lázaro y Pablo Galera Morcillo
	 *************************************************************************/
  private void jbInit() throws Exception {

    this.setLayout(new MiLayout());
    jlblreq1.setForeground(Color.red);
    jlblreq1.setBounds(new Rectangle(15, 30, 10, 20));
    jlblId.setText("VariableId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jtxtId.setPreferredSize(new Dimension(400, 20));
    jtxtId.setLocation(135, 30);
    jtxtId.setText(elemento.getID());
    jtxtId.addKeyListener(new MiElementKeyAdapter(this));

    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 60, 100, 20));
    this.add(jlblreq1);
    this.add(jlblrequerido);
    this.add(jlblId);
    this.add(jtxtId);
  }

  public void keyReleased(KeyEvent e) {
    if (e.getSource() == jtxtId) {
      Map at = elemento.getAtributos();
      at.remove("VariableId");
      at.put("VariableId", jtxtId.getText());
    }
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }

}
