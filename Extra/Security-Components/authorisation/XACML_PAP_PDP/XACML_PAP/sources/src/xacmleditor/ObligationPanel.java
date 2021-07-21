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
import javax.swing.border.EtchedBorder;
import javax.swing.border.TitledBorder;
import javax.swing.event.ListSelectionEvent;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;
import java.awt.event.ItemEvent;
import java.awt.event.KeyEvent;
import java.util.*;

/* *************************************************************************
 * Title: ObligationPanel
 *
 * Description:*//** This panel is used for setting up a Obligation Element.
 *
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 *
 * @version 1.3
 ***************************************************************************/
public class ObligationPanel
    extends ElementPanel implements Observer {

  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JComboBox jcmbEffect = new JComboBox(ElementoXACML.getAllEffects());
  JLabel jlblEffect = new JLabel();
  JScrollPane jscrllPanel;
  JList lista = new JList();
  ElementPanel panelActual;
  JPanel panelLista = new JPanel(new MiLayout());
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblreq2 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public ObligationPanel(DefaultMutableTreeNode n) {
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
    jlblId.setText("ObligationId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jtxtId.setLocation(135, 30);
    jtxtId.setPreferredSize(new Dimension(315, 20));
    jtxtId.setText(elemento.getID());
    jtxtId.addKeyListener(new MiElementKeyAdapter(this));

    jlblreq2.setForeground(Color.red);
    jlblreq2.setBounds(new Rectangle(15, 60, 10, 20));
    jlblEffect.setText("FulfillOn:");
    jlblEffect.setBounds(new Rectangle(25, 60, 100, 20));
    jcmbEffect.setLocation(135, 60);
    jcmbEffect.setPreferredSize(new Dimension(75, 20));
    jcmbEffect.setEditable(true);
    jcmbEffect.setSelectedItem( (String) elemento.getAtributos().get(
        "FulfillOn"));
    jcmbEffect.addItemListener(new MiElementItemAdapter(this));
    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 230, 100, 20));

    this.add(jlblreq1);
    this.add(jlblreq2);
    this.add(jlblrequerido);
    this.add(jlblId);
    this.add(jtxtId);
    this.add(jcmbEffect);
    this.add(jlblEffect);

    lista.addListSelectionListener(new MiListSelectionAdapter(this));
    jscrllPanel = new JScrollPane(lista);
    jscrllPanel.setAutoscrolls(true);
    jscrllPanel.setLocation(5, 90);
    jscrllPanel.setPreferredSize(new Dimension(450, 120));
    TitledBorder miborde = new TitledBorder(new EtchedBorder(),
    										// JR
                                            //"Lista de AttributeAssignment");
    										"List of AttributeAssignment");
    										// JREND
    jscrllPanel.setBorder(miborde);
    panelLista.add(jscrllPanel);

    actualizar();
    this.add(panelLista);
  }

  public void update(Observable o, Object arg) {
    int g = lista.getSelectedIndex();
    actualizar();
    lista.setSelectedIndex(g);
  }

  public void actualizar() {
    Enumeration subelementos = nodo.children();
    Vector vec = new Vector();
    while (subelementos.hasMoreElements()) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) subelementos.
          nextElement();
      if (aux.getUserObject() instanceof ElementoAttributeAssignment) {
        vec.add(aux);
      }
    }
    lista.setListData(vec);
  }

  public void keyReleased(KeyEvent e) {

    if (e.getSource() == jtxtId) {
      Map at = elemento.getAtributos();
      at.remove("ObligationId");
      at.put("ObligationId", jtxtId.getText());
    }
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }

  public void itemStateChanged(ItemEvent e) {
    Map mapa = elemento.getAtributos();
    mapa.put("FulfillOn", (String) jcmbEffect.getSelectedItem());
    elemento.setAtributos(mapa);
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }

  public void setTreeModel(DefaultTreeModel tm) {
    super.setTreeModel(tm);
    dtm.addTreeModelListener(new MiTreeModelAdapter(this));
  }

  public void valueChanged(ListSelectionEvent e) {
    if (panelActual != null) {
      this.remove(panelActual);
      ((AttributeAssignmentPanel) panelActual).deleteObserver(this);

    }
    if (lista != null) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) lista.
          getSelectedValue();

      panelActual = XACMLPanelFactoryImpl.getInstance().obtenerPanel(aux);
      if (panelActual != null) {
        if (panelActual instanceof AttributeAssignmentPanel) {
          ( (AttributeAssignmentPanel) panelActual).addObserver(this);
          TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
              "AttributeAssignment");
          panelActual.setBorder(miborde2);
          panelActual.setLocation(0, 250);
          panelActual.setTreeModel(dtm);
          this.add(panelActual);
        }else panelActual=null;
      }
    }
    this.validate();
    this.repaint();
  }

}


