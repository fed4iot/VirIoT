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
import java.awt.event.ActionEvent;
import java.util.Hashtable;

/**
 * This panel permites commute betwenn panels.And extends of the ElementPanel
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class ConmutadorPanel
    extends ElementPanel {

  ButtonGroup bttnGrupo = new ButtonGroup();
  JRadioButton jrbSelector = new JRadioButton();
  JRadioButton jrbDesignator = new JRadioButton();
  ElementPanel panelActual;

  public ConmutadorPanel(DefaultMutableTreeNode n) {
    super(n);
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  public void setTreeModel(DefaultTreeModel d) {
    super.setTreeModel(d);
    panelActual.setTreeModel(dtm);
  }

  private void jbInit() throws Exception {
    this.setLayout(new MiLayout());
    this.setPreferredSize(new Dimension(570, 250));
    jrbSelector.setText("Attribute Selector");
    jrbSelector.setBounds(new Rectangle(50, 20, 130, 20));
    jrbSelector.addActionListener(new MiElementActionAdapter(this));
    jrbDesignator.setText("Attribute Designator");
    jrbDesignator.setBounds(new Rectangle(180, 20, 130, 20));
    jrbDesignator.addActionListener(new MiElementActionAdapter(this));
    bttnGrupo.add(jrbDesignator);
    bttnGrupo.add(jrbSelector);
    this.add(jrbSelector);
    this.add(jrbDesignator);
    if (elemento instanceof ElementoAttributeDesignator) {
      jrbDesignator.setSelected(true);
      panelActual = new AttributeDesignatorPanel(nodo);
    }
    else if (elemento instanceof ElementoAttributeSelector) {
      jrbSelector.setSelected(true);
      panelActual = new AttributeSelectorPanel(nodo);
    }
    else {
      panelActual = new ElementPanel(nodo);
    }
    TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
              "<"+elemento.getTipo()+">");
    panelActual.setBorder(miborde2);
    panelActual.setLocation(5, 50);
    this.add(panelActual);
  }

  public void actionPerformed(ActionEvent e) {
    String nuevoTipo = "";
    if (e.getSource() == jrbSelector) {
      nuevoTipo = "AttributeSelector";
    }
    else {
      ElementoXACML elem=(ElementoXACML)((DefaultMutableTreeNode)nodo.getParent()).getUserObject();
      nuevoTipo =  elem.getTipo().replaceFirst("Match","")+"AttributeDesignator";
    }

    elemento = ElementoXACMLFactoryImpl.getInstance().obtenerElementoXACML(
        nuevoTipo, new Hashtable());
      elemento.setVacio(true);
    nodo.setUserObject(elemento);
    this.remove(panelActual);

    if (e.getSource() == jrbSelector) {
      panelActual = new AttributeSelectorPanel(nodo);
    }
    else {
      panelActual = new AttributeDesignatorPanel(nodo);
    }
    TitledBorder miborde2 = new TitledBorder(new EtchedBorder(),
              "<"+elemento.getTipo()+">");
          panelActual.setBorder(miborde2);

    panelActual.setLocation(5, 50);
    panelActual.setTreeModel(dtm);
    this.add(panelActual);
    this.validate();
    this.repaint();
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }
}
