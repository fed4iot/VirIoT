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
import java.awt.event.KeyEvent;
import java.util.Map;


/** It's a panel for editing the AttributeAssignment elements of the XACML 2.0 standard
 *
 * @author Albero Jimenez Lazaro & Pablo Galera Morcillo
 * @version 1.3
 */
public class AttributeAssignmentPanel
    extends ElementPanel {

  JLabel jlblDataType = new JLabel();
  JLabel jlblAttributeId = new JLabel();
  JComboBox jcmbDataType = new JComboBox(ElementoXACML.getAllDataTypes());
  JComboBox jcmbAttributeId = new JComboBox(ElementoXACML.getAllAttributeId());
  JLabel jblContenido = new JLabel();
  JTextField jtxtContenido = new JTextField();

  public AttributeAssignmentPanel(DefaultMutableTreeNode n) {
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
    
    jlblAttributeId.setText("AttributeId:");
    jlblAttributeId.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbAttributeId.setPreferredSize(new Dimension(400, 20));
    jcmbAttributeId.setLocation(135,30);
    jcmbAttributeId.setEditable(true);
    jcmbAttributeId.setSelectedItem( (String) elemento.getID());
    jcmbAttributeId.addItemListener(new MiElementItemAdapter(this));
    jlblDataType.setText("Data Type:");
    jlblDataType.setBounds(new Rectangle(25, 60, 100, 20));
    jcmbDataType.setEditable(true);
    jcmbDataType.setSelectedItem( ( (ElementoAttributeAssignment) elemento).
                                 getDataType());
    jcmbDataType.setPreferredSize(new Dimension(400, 20));
    jcmbDataType.setLocation(135,60);
    jcmbDataType.addItemListener(new MiElementItemAdapter(this));

    jblContenido.setText("Value:");
    jblContenido.setBounds(new Rectangle(25, 90, 100, 20));
    jtxtContenido.setText(elemento.getContenido());
    jtxtContenido.setPreferredSize(new Dimension(400, 20));
    jtxtContenido.setLocation(135,90);
    jtxtContenido.addKeyListener(new MiElementKeyAdapter(this));

    this.add(jlblAttributeId);
    this.add(jcmbAttributeId);
    this.add(jlblDataType);
    this.add(jcmbDataType);
    this.add(jblContenido);
    this.add(jtxtContenido);
  }

  public void keyReleased(KeyEvent e) {
    elemento.setContenido(jtxtContenido.getText());
    if(dtm!=null) dtm.nodeChanged(nodo);
  }
  public void itemStateChanged(ItemEvent e) {
    if (e.getSource() == jcmbDataType) {
      ( (ElementoAttributeAssignment) elemento).setDataType( (String)
          jcmbDataType.getSelectedItem());
    }
    else if (e.getSource() == jcmbAttributeId) {
      Map mapa = elemento.getAtributos();
      mapa.remove("AttributeId");
      mapa.put("AttributeId", (String) jcmbAttributeId.getSelectedItem());
      elemento.setAtributos(mapa);
   }
    miobservable.cambiar(nodo);
    if (dtm != null) {
     dtm.nodeChanged(nodo);
    }
  }
}
