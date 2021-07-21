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
import java.util.Enumeration;
import java.util.Observable;
import java.util.Observer;
import java.util.Vector;

/** This panel is used to showing the Action, Subject or Resource elements.
 * The panel show a list of (Action,Subject,Resource)Match.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class ListaPanel
    extends ElementPanel implements Observer {

  JScrollPane jscrllPanel;
  JList lista = new JList();
  ElementPanel panelActual;
  JPanel panelLista = new JPanel(new MiLayout());


  public ListaPanel(DefaultMutableTreeNode n) {
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

    lista.addListSelectionListener(new MiListSelectionAdapter(this));
    jscrllPanel = new JScrollPane(lista);
    jscrllPanel.setAutoscrolls(true);
    jscrllPanel.setLocation(5, 30);
    jscrllPanel.setPreferredSize(new Dimension(450, 120));
    TitledBorder miborde = new TitledBorder(new EtchedBorder(),
    										// JR English
                                            // "Lista de " + elemento.getTipo() +
    		 								"List of " + elemento.getTipo() +
                                            // JREND
                                             "Match");
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
      if (aux.getUserObject() instanceof ElementoMatch) {
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
          if (panelActual instanceof MatchPanel) {
            panelActual.addObserver(this);
            TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
                elemento.getTipo() +"Match");
            panelActual.setBorder(miborde2);
            panelActual.setLocation(0, 180);
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




