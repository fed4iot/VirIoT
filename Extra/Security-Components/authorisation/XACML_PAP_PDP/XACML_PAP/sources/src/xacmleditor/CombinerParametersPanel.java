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
import java.awt.event.KeyEvent;
import java.util.*;


/**Element CombinerParametersPanel. This panel contains a list and
 * a child panel inside of it. This panel is related with an item
 * which has been selected in the list.
 *
 * @author Alberto Jiménez Lázaro, Pablo Galera Morcillo
 *
 */
public class CombinerParametersPanel
    extends ElementPanel implements Observer {

  JScrollPane jscrllPanel;
  JList lista = new JList();
  ElementPanel panelActual;
  JPanel panelLista = new JPanel(new MiLayout());
  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  String tipo;
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public CombinerParametersPanel(DefaultMutableTreeNode n) {
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
    int sumatorio=30;
    if(elemento.getTipo()!="CombinerParameters"){
      jlblreq1.setForeground(Color.red);
      jlblreq1.setBounds(new Rectangle(15, sumatorio, 10, 20));
      //todo modificado
      tipo=elemento.getTipo().replaceAll("CombinerParameters","") + "IdRef";
      jlblId.setText(tipo + ":");
      jlblId.setBounds(new Rectangle(25, sumatorio, 100, 20));
      jtxtId.setText(elemento.getID());
      jtxtId.setLocation(135, sumatorio);
      jtxtId.setPreferredSize(new Dimension(400, 20));
      jtxtId.addKeyListener(new MiElementKeyAdapter(this));
      sumatorio+=30;
      jlblrequerido.setForeground(Color.red);
      jlblrequerido.setBounds(new Rectangle(135, sumatorio, 100, 20));
      sumatorio+=30;
      this.add(jlblId);
      this.add(jtxtId);
      this.add(jlblreq1);
      this.add(jlblrequerido);
    }

    lista.addListSelectionListener(new MiListSelectionAdapter(this));
    jscrllPanel = new JScrollPane(lista);
    jscrllPanel.setAutoscrolls(true);
    jscrllPanel.setLocation(5, sumatorio);
    jscrllPanel.setPreferredSize(new Dimension(450, 120));
    TitledBorder miborde = new TitledBorder(new EtchedBorder(),
                                             "List of " + elemento.getTipo());
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

  public void keyReleased(KeyEvent e) {
    Map mapa = elemento.getAtributos();
    mapa.remove(tipo);
    mapa.put(tipo, jtxtId.getText());
      elemento.setAtributos(mapa);
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }
  public void actualizar() {
    Enumeration subelementos = nodo.children();
    Vector vec = new Vector();
    while (subelementos.hasMoreElements()) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) subelementos.
          nextElement();
      if (aux.getUserObject() instanceof ElementoCombinerParameter) {
        vec.add(aux);
      }
    }
    lista.setListData(vec);
  }

    public void valueChanged(ListSelectionEvent e) {
      if (panelActual != null) {
        this.remove(panelActual);
        panelActual.deleteObserver(this);
      }
      if(lista!=null){
        DefaultMutableTreeNode aux = (DefaultMutableTreeNode) lista.
            getSelectedValue();

        panelActual = XACMLPanelFactoryImpl.getInstance().obtenerPanel(aux);
        if (panelActual != null) {
          if (panelActual instanceof CombinerParameterPanel) {
            panelActual.addObserver(this);
            TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
                elemento.getTipo());
            panelActual.setBorder(miborde2);
            panelActual.setLocation(0, 220);
            panelActual.setTreeModel(dtm);
            this.add(panelActual);
          }
          else panelActual = null;
        }
      }
      this.validate();
      this.repaint();
   }

   public void setTreeModel(DefaultTreeModel tm) {
     super.setTreeModel(tm);
     dtm.addTreeModelListener(new MiTreeModelAdapter(this));
   }


 }
