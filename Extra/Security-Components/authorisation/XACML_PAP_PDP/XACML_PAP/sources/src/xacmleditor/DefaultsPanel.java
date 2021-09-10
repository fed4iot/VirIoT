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
import java.awt.event.KeyEvent;
import java.util.Enumeration;
import java.util.Hashtable;


/**
 * This is the default Panel.
 * @author Alberto Jiménez Lázaro & Pablo Galera Morcillo
 * @version 1.3
 */
public class DefaultsPanel
    extends ElementPanel {

  JLabel jblXpath = new JLabel();
  JTextField jtxtXpath = new JTextField();
  ElementoXPathVersion XPathVersion;


  public DefaultsPanel(DefaultMutableTreeNode n) {
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
    this.setPreferredSize(new Dimension(500, 70));
    jblXpath.setText("XPathVersion:");
    jblXpath.setBounds(new Rectangle(25, 30, 100, 20));

    Enumeration subelementos = nodo.children();
    while (subelementos.hasMoreElements()) {
      DefaultMutableTreeNode aux = (DefaultMutableTreeNode) subelementos.
          nextElement();
      Object eaux = aux.getUserObject();
      if (eaux instanceof ElementoXPathVersion) {
        XPathVersion = (ElementoXPathVersion) eaux;
        jtxtXpath.setText( ( (ElementoXPathVersion) eaux).getContenido());
      }
    }
    jtxtXpath.addKeyListener(new MiElementKeyAdapter(this));
    jtxtXpath.setPreferredSize(new Dimension(400, 20));
    jtxtXpath.setLocation(135, 30);
    this.add(jblXpath);
    this.add(jtxtXpath);
  }

  public void keyReleased(KeyEvent e) {
    if (e.getSource() == jtxtXpath) {
      if (XPathVersion == null) {
         XPathVersion = (ElementoXPathVersion) ElementoXACMLFactoryImpl.
             getInstance().
             obtenerElementoXACML("XPathVersion", new Hashtable());

         DefaultMutableTreeNode naux = new DefaultMutableTreeNode(XPathVersion);
         dtm.insertNodeInto(naux, nodo, 0);
       }
       XPathVersion.setContenido(jtxtXpath.getText());

    }
    if(dtm!=null) dtm.nodeChanged(nodo);
  }
}
