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
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;
import java.awt.event.ItemEvent;
import java.util.Map;


/** It's a panel for editing the CombinerParameter elements of the XACML 2.0 standard
 *
 * @author Albero Jimenez Lazaro & Pablo Galera Morcillo
 * @version 1.3
 */
public class CombinerParameterPanel
  extends ElementPanel {

  JLabel jlblId = new JLabel();
  JComboBox jcmbtxtId = new JComboBox(ElementoXACML.getAllParamName());
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");
  CombiPanel cp;

  public CombinerParameterPanel(DefaultMutableTreeNode n) {
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
    jlblId.setText("ParameterName:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbtxtId.setPreferredSize(new Dimension(400, 20));
    jcmbtxtId.setLocation(135, 30);
    jcmbtxtId.setEditable(true);
    jcmbtxtId.setSelectedItem(elemento.getID());
    jcmbtxtId.addItemListener(new MiElementItemAdapter(this));
    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 60, 100, 20));

    this.add(jlblId);
    this.add(jcmbtxtId);
    this.add(jlblreq1);
    this.add(jlblrequerido);

    cp = new CombiPanel(nodo);
    cp.setLocation(5, 110);
    this.add(cp);
  }

  public void setTreeModel(DefaultTreeModel d) {
    super.setTreeModel(d);
    cp.setTreeModel(dtm);
  }

  public void itemStateChanged(ItemEvent e) {
     if (e.getSource() == jcmbtxtId) {
      Map mapa = elemento.getAtributos();
      mapa.remove("ParameterName");
      mapa.put("ParameterName", (String) jcmbtxtId.getSelectedItem());
      elemento.setAtributos(mapa);
   }
    miobservable.cambiar(nodo);
    if (dtm != null) {
     dtm.nodeChanged(nodo);
    }
  }

}
