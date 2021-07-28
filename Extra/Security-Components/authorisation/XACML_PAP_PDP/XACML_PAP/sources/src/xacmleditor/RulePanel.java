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
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Map;

/* ******************************************************************
 * Title: RulePanel
 *
 * Description: *//** This panel is used for setting up a Rule
 * element.
 *
 *
 * @author Alberto Jimenez Lazaro y Pablo Galera Morcillo
 * @version 1.3
 *******************************************************************/
public class RulePanel
    extends ElementPanel {

  JScrollPane jscrllPanel;
  JLabel jlblId = new JLabel();
  JTextField jtxtId = new JTextField();
  JComboBox jcmbEffect = new JComboBox(ElementoXACML.getAllEffects());
  JLabel jlblEffect = new JLabel();
  JLabel jlblreq1 = new JLabel("*");
  JLabel jlblreq2 = new JLabel("*");
  JLabel jlblrequerido = new JLabel("* Required");
  JLabel jlblDescription = new JLabel();
  JTextArea jtxtaDescription = new JTextArea();
  ElementoDescription descripcion;

  public RulePanel(DefaultMutableTreeNode n) {
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
    jlblId.setText("RuleId:");
    jlblId.setBounds(new Rectangle(25, 30, 100, 20));
    jtxtId.setText(elemento.getID());
    jtxtId.setLocation(135,30);
    jtxtId.setPreferredSize(new Dimension(450, 20));
    jtxtId.addKeyListener(new MiElementKeyAdapter(this));

    jlblreq2.setForeground(Color.red);
    jlblreq2.setBounds(new Rectangle(15, 60, 10, 20));
    jlblEffect.setText("Effect:");
    jlblEffect.setBounds(new Rectangle(25, 60, 100, 20));
    jcmbEffect.setLocation(135,60);
    jcmbEffect.setPreferredSize(new Dimension(450, 20));
    jcmbEffect.setEditable(true);
    jcmbEffect.setSelectedItem((String)elemento.getAtributos().get("Effect"));
    jcmbEffect.addItemListener(new MiElementItemAdapter(this));

    jlblDescription.setText("Description:");
    jlblDescription.setBounds(new Rectangle(25, 90, 100, 20));

    Enumeration subelementos=nodo.children();
    while(subelementos.hasMoreElements()){
      DefaultMutableTreeNode aux=(DefaultMutableTreeNode)subelementos.nextElement();
      Object eaux=aux.getUserObject();
      if(eaux instanceof ElementoDescription){
        descripcion = (ElementoDescription) eaux;
        jtxtaDescription.setText(((ElementoDescription)eaux).getContenido());
      }

    }
    jtxtaDescription.addKeyListener(new MiElementKeyAdapter(this));

    jscrllPanel=new JScrollPane(jtxtaDescription);
    jscrllPanel.setAutoscrolls(true);
    jscrllPanel.setLocation(135,90);
    jscrllPanel.setPreferredSize(new Dimension(450, 120));
    jlblrequerido.setForeground(Color.red);
    jlblrequerido.setBounds(new Rectangle(135, 230, 100, 20));

    this.add(jlblreq1);
    this.add(jlblreq2);
    this.add(jlblrequerido);

    this.add(jlblId);
    this.add(jtxtId);
    this.add(jcmbEffect);
    this.add(jlblEffect);
    this.add(jlblDescription);
    this.add(jscrllPanel);
  }

  public void keyReleased(KeyEvent e) {

    if (e.getSource() == jtxtId) {
      Map at = elemento.getAtributos();
      at.remove("RuleId");
      at.put("RuleId", jtxtId.getText());
    }
    else if (e.getSource() == jtxtaDescription){

        // Puede que no exista un elemento Description
        if (descripcion == null) {
          descripcion = (ElementoDescription) ElementoXACMLFactoryImpl.
              getInstance().
              obtenerElementoXACML("Description", new Hashtable());

          DefaultMutableTreeNode naux = new DefaultMutableTreeNode(descripcion);
          dtm.insertNodeInto(naux, nodo, 0);
        }
        descripcion.setContenido(jtxtaDescription.getText());
    }
    if (dtm != null) {
      dtm.nodeChanged(nodo);
    }
  }

  public void itemStateChanged(ItemEvent e) {
    Map mapa=elemento.getAtributos();
    mapa.put("Effect",(String)jcmbEffect.getSelectedItem());
    elemento.setAtributos(mapa);
    if(dtm!=null) dtm.nodeChanged(nodo);
  }

}
