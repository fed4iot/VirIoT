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

import javax.swing.border.EtchedBorder;
import javax.swing.border.TitledBorder;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import java.util.Enumeration;


/* ****************************************************************
 * Title: CombiPanel
 *
 * Description:*//** This panel is made up of severals panels
 * which correspond with the panels of its child nodes.
 * This panel is used for
 *
 * @author Alberto Jiménez Lázaro & Pablo Galera Morcillo
 *
 * @version 1.3
 ***************************************************************/
public class CombiPanel
    extends ElementPanel {

  ElementPanel panelActual;
  int contador;
  public CombiPanel(DefaultMutableTreeNode n) {
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
    Enumeration subelementos=nodo.children();
    contador=0;
    int anyadido=0;
    while(subelementos.hasMoreElements()){
      DefaultMutableTreeNode aux=(DefaultMutableTreeNode)subelementos.nextElement();
      panelActual=XACMLPanelFactoryImpl.getInstance().obtenerPanel(aux);
      if(panelActual!=null) {
        ElementoXACML elem= (ElementoXACML)aux.getUserObject();
        TitledBorder miborde2;
        if(elem instanceof ElementoAttributeSelector || elem instanceof ElementoAttributeDesignator)
           miborde2 = new TitledBorder(new EtchedBorder(),"Choice");
          else miborde2 = new TitledBorder(new EtchedBorder(),
                                      "<" + elem.getTipo() + ">");

       panelActual.setBorder(miborde2);
       panelActual.setLocation(0, anyadido);
       this.add(panelActual);
       anyadido+=getComponent(contador).getPreferredSize().height + 30;
       contador++;
      }
    }
  }

  public int getNumberHijos(){
    return contador;
  }

  public void setTreeModel(DefaultTreeModel d){
    super.setTreeModel(d);
    for(int i=0;i<this.getComponentCount();i++){
      if(getComponent(i) instanceof ElementPanel){
        ((ElementPanel)getComponent(i)).setTreeModel(d);
      }
    }
  }


}

