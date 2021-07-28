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


/** It's a panel for editing the AttributeValue elements of the XACML 2.0 standard
*
* @author Albero Jimenez Lazaro & Pablo Galera Morcillo
* @version 1.3
*/
public class AttributeValuePanel
    extends ElementPanel {

  JLabel jlblDataType = new JLabel();
  JComboBox jcmbDataType = new JComboBox(ElementoXACML.getAllDataTypes());
  JLabel jblContenido = new JLabel();
  // JR
  JComboBox jcmbContenido = new JComboBox(ElementoXACML.getPossibleAttributeValues());
  //JTextField jtxtContenido = new JTextField();
  // JREND
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public AttributeValuePanel(DefaultMutableTreeNode n) {
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
    this.setPreferredSize(new Dimension(550, 120));

    jlblreq1.setForeground(Color.red);
    jlblreq1.setBounds(new Rectangle(15, 30, 10, 20));
    jlblDataType.setText("Data Type:");
    jlblDataType.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbDataType.setEditable(true);
    jcmbDataType.setPreferredSize(new Dimension(400, 20));
    jcmbDataType.setLocation(135, 30);
    jcmbDataType.setSelectedItem( ( (ElementoAttributeValue) elemento).
                                 getDataType());
    jcmbDataType.addItemListener(new MiElementItemAdapter(this));
    jblContenido.setText("Value:");
    jblContenido.setBounds(new Rectangle(25, 60, 100, 20));
    jcmbContenido.setEditable(true);
    jcmbContenido.setSelectedItem( elemento.getContenido());
    jcmbContenido.setPreferredSize(new Dimension(400, 20));
    jcmbContenido.setLocation(135,60);
    jcmbContenido.addItemListener(new MiElementItemAdapter(this));
    //jtxtContenido.setText(elemento.getContenido());
    //jtxtContenido.setPreferredSize(new Dimension(400, 20));
    //jtxtContenido.setLocation(135, 60);
    //jtxtContenido.addKeyListener(new MiElementKeyAdapter(this));

    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 90, 100, 20));

    this.add(jblContenido);
    // JR
    this.add(jcmbContenido);
    //this.add(jtxtContenido);
    // JREND
    this.add(jcmbDataType);
    this.add(jlblDataType);
    this.add(jlblreq1);
    this.add(jlblrequerido);
  }

  public void keyReleased(KeyEvent e) {
	// JR
    //elemento.setContenido(jtxtContenido.getText());
    //if(dtm!=null) dtm.nodeChanged(nodo);
	// JREND
  }

  public void itemStateChanged(ItemEvent e) {
	// JR
	if (e.getSource() == jcmbDataType) {
	// ENDJR
    ( (ElementoAttributeValue) elemento).setDataType( (String) jcmbDataType.
        getSelectedItem());
    // JR
	}
    else if (e.getSource() == jcmbContenido) {
    	elemento.setContenido((String) jcmbContenido.getSelectedItem());
    }
    // ENDJR
    miobservable.cambiar(nodo);
    if(dtm!=null) dtm.nodeChanged(nodo);
  }
}
