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
import java.util.*;


/* ****************************************************************
* Title: ApplyPanel
*
* Description:*//** This is the panel for editing Apply Elements.
 *
 * @author Alberto Jiménez Lázaro & Pablo Galera Morcillo
 *
 * @version 1.3
 ***************************************************************/
public class ApplyPanel
    extends ElementPanel implements Observer{

  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JComboBox jcmbIdFunction = new JComboBox(ElementoXACML.getAllFunctions());
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  JScrollPane jscrllPanel1;
  JList lista1 = new JList();
  JPanel panelLista1 = new JPanel();
  JScrollPane jscrllPanel2;
  JList lista2 = new JList();
  JPanel panelLista2 = new JPanel();
  ElementPanel panelActual;

  public ApplyPanel(DefaultMutableTreeNode n) {
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
    this.setPreferredSize(new Dimension(580, 600));
    jlblreq1.setForeground(Color.red);
    jlblreq1.setBounds(new Rectangle(15, 30, 10, 20));
    jlblId.setText("FunctionId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbIdFunction.setPreferredSize(new Dimension(400, 20));
    jcmbIdFunction.setLocation(135, 30);
    jcmbIdFunction.setEditable(true);
    jcmbIdFunction.setSelectedItem( (String) elemento.getID());
    jcmbIdFunction.addItemListener(new MiElementItemAdapter(this));
    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 60, 100, 20));
    this.add(jlblreq1);
    this.add(jlblrequerido);
    this.add(jlblId);
    this.add(jcmbIdFunction);

    jscrllPanel1 = new JScrollPane(lista1);
    lista1.setEnabled(false);
    jscrllPanel1.setAutoscrolls(true);
    jscrllPanel1.setPreferredSize(new Dimension(515, 140));
    jscrllPanel1.setLocation(25, 90);
    TitledBorder miborde1 = new TitledBorder(new EtchedBorder(),
                                             "List of Applies");
    jscrllPanel1.setBorder(miborde1);
    panelLista1.add(jscrllPanel1);
    panelLista1.setPreferredSize(new Dimension(525, 150));
    panelLista1.setLocation(25, 90);
    this.add(panelLista1);


    jscrllPanel2 = new JScrollPane(lista2);
    lista2.addListSelectionListener(new MiListSelectionAdapter(this));
    jscrllPanel2.setAutoscrolls(true);
    jscrllPanel2.setPreferredSize(new Dimension(515, 140));
    jscrllPanel2.setLocation(25, 240);
    TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
                                            "List of Simple Expresions");
    jscrllPanel2.setBorder(miborde2);
    panelLista2.add(jscrllPanel2);
    panelLista2.setPreferredSize(new Dimension(525, 150));
    panelLista2.setLocation(25, 240);
    this.add(panelLista2);
    actualizar();
  }

  
public void actualizar() {
    Enumeration subelementos = nodo.children();
    Vector vec1 = new Vector();
    Vector vec2 = new Vector();
    while (subelementos.hasMoreElements()) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) subelementos.
          nextElement();
      if (aux.getUserObject() instanceof ElementoApply) {
        vec1.add(aux);
      }
      else if (elemento.isAllowedChild( (ElementoXACML) aux.getUserObject())) {
        vec2.add(aux);
      }
    }
    lista1.setListData(vec1);
    lista2.setListData(vec2);
  }

  public void valueChanged(ListSelectionEvent e) {
    if (panelActual != null) {
      this.remove(panelActual);
      panelActual.deleteObserver(this);
    }
    if(lista2!=null){
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) lista2.
          getSelectedValue();

      panelActual = XACMLPanelFactoryImpl.getInstance().obtenerPanel(aux);
      if (panelActual != null) {
        panelActual.addObserver(this);
        ElementoXACML elemHijo=(ElementoXACML)aux.getUserObject();
          TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
               elemHijo.getTipo());
          panelActual.setBorder(miborde2);
          panelActual.setLocation(15, 410);
          panelActual.setTreeModel(dtm);
          this.add(panelActual);
      }
    }
    this.validate();
    this.repaint();
   }

  public void update(Observable o, Object arg) {
  int g = lista2.getSelectedIndex();
  actualizar();
  lista2.setSelectedIndex(g);
}

  public void setTreeModel(DefaultTreeModel d) {
    super.setTreeModel(d);
    dtm.addTreeModelListener(new MiTreeModelAdapter(this));
  }

  public void itemStateChanged(ItemEvent e) {
    Map mapa = elemento.getAtributos();
    mapa.put("FunctionId", (String) jcmbIdFunction.getSelectedItem());
    elemento.setAtributos(mapa);
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }
}


