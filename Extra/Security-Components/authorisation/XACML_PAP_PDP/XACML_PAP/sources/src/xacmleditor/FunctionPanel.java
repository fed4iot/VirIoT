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
import java.awt.event.ItemEvent;
import java.util.Map;

/** This panel is used for showing the Function elements.
*
* @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
* @version 1.3
*/
public class FunctionPanel
    extends ElementPanel {

  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JComboBox jcmbIdFunction = new JComboBox(ElementoXACML.getAllFunctions());
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public FunctionPanel(DefaultMutableTreeNode n) {
    super(n);
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  private void jbInit() throws Exception {

    this.setLayout(new MiLayout());
    jlblreq1.setForeground(Color.red);
    jlblreq1.setBounds(new Rectangle(15, 30, 10, 20));
    jlblId.setText("FunctionId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbIdFunction.setPreferredSize(new Dimension(400, 20));
    jcmbIdFunction.setLocation(135, 30);
    jcmbIdFunction.setEditable(true);
    jcmbIdFunction.setSelectedItem( (String) elemento.getAtributos().get(
        "FunctionId"));
    jcmbIdFunction.addItemListener(new MiElementItemAdapter(this));

    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 60, 100, 20));
    this.add(jlblreq1);
    this.add(jlblrequerido);
    this.add(jlblId);
    this.add(jcmbIdFunction);
  }

  public void itemStateChanged(ItemEvent e) {
    Map mapa = elemento.getAtributos();
    mapa.put("FunctionId", (String) jcmbIdFunction.getSelectedItem());
    elemento.setAtributos(mapa);
    miobservable.cambiar(nodo);
      if (dtm != null) {
        dtm.nodeChanged(nodo);
      }
   }
}
