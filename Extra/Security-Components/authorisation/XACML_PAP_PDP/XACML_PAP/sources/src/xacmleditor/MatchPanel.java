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
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import java.awt.*;
import java.awt.event.ItemEvent;
import java.util.Enumeration;
import java.util.Map;

/* *************************************************************************
 * Title: MatchPanel
 *
 * Description:*//** This panel is used for setting up a Match element.
 *
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 *
 * @version 1.3
 ***************************************************************************/
public class MatchPanel
    extends ElementPanel {

  JLabel jlblId = new JLabel();
  JComboBox jcmbIdFunction = new JComboBox(ElementoXACML.getAllFunctions());
  ElementPanel panelActual;
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");

  public MatchPanel(DefaultMutableTreeNode n) {
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
    jlblId.setText("MatchId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jcmbIdFunction.setPreferredSize(new Dimension(400, 20));
    jcmbIdFunction.setLocation(135, 30);
    jcmbIdFunction.setEditable(true);
    jcmbIdFunction.setSelectedItem( (String) elemento.getID());
    jcmbIdFunction.addItemListener(new MiElementItemAdapter(this));
    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 60, 100, 20));
    this.add(jlblId);
    this.add(jcmbIdFunction);
    this.add(jlblreq1);
    this.add(jlblrequerido);

    Enumeration subelementos = nodo.children();

    int anyadido=90;
    while (subelementos.hasMoreElements()) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) subelementos.
          nextElement();
      panelActual = XACMLPanelFactoryImpl.getInstance().obtenerPanel(aux);
      if (panelActual != null) {
        ElementoXACML elem = (ElementoXACML) aux.getUserObject();

        TitledBorder miborde2;
        if (elem instanceof ElementoAttributeSelector ||
            elem instanceof ElementoAttributeDesignator) {
          miborde2 = new TitledBorder(new EtchedBorder(), "Choice");
          panelActual=new ConmutadorPanel(aux);
        }
        else {
          miborde2 = new TitledBorder(new EtchedBorder(),
                                      "<" + elem.getTipo() + ">");
        }
        panelActual.setBorder(miborde2);
        panelActual.setLocation(5, anyadido);
        this.add(panelActual);
        anyadido+=panelActual.getPreferredSize().height + 30;
      }
    }

  }

  public void setTreeModel(DefaultTreeModel d){
    super.setTreeModel(d);
    for(int i=0;i<this.getComponentCount();i++){
      if(getComponent(i) instanceof ElementPanel){
        ((ElementPanel)getComponent(i)).setTreeModel(d);
      }
    }
  }

  public void itemStateChanged(ItemEvent e) {
    Map mapa = elemento.getAtributos();
    mapa.put("MatchId", (String) jcmbIdFunction.getSelectedItem());
    elemento.setAtributos(mapa);
    miobservable.cambiar(nodo);
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }
}
