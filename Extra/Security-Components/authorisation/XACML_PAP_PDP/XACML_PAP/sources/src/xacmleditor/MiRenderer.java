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
import javax.swing.tree.DefaultTreeCellRenderer;
import java.awt.*;


/**
 * This is an implemtation of the DefaultTreeCellRenderer class that is used to paint the Tree cells
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class MiRenderer
    extends DefaultTreeCellRenderer {


   private ImageIcon cara;
   private ImageIcon rule;
   private ImageIcon verde;
   private ImageIcon nube;


  public MiRenderer() {
    super();
    try{

      cara = createImageIcon("icons/cara.gif");
      rule = createImageIcon("icons/target.gif");
      verde = createImageIcon("icons/verde.gif");
      nube = createImageIcon("icons/nube.gif");

    }catch(java.net.MalformedURLException e){
    }
  }

  protected ImageIcon createImageIcon(String path)
          throws java.net.MalformedURLException {

      // JR: use .getClassLoader()'s getResource, so it finds multi-level path resource name
      java.net.URL imgURL= getClass().getClassLoader().getResource(path);      

      // JREND
      if (imgURL != null) {
          return new ImageIcon(imgURL);
      } else {
          System.err.println("Couldn't find file: " + path);
          return null;
      }
}
  /**
   * Sets the value of the current tree cell to <code>value</code>.
   *
   * @return the <code>Component</code> that the renderer uses to draw the
   *   value
   * @param tree JTree
   * @param value Object
   * @param sel boolean
   * @param expanded boolean
   * @param leaf boolean
   * @param row int
   * @param hasFocus boolean
   * todo Implement this javax.swing.tree.TreeCellRenderer method
   */
  public Component getTreeCellRendererComponent(JTree tree, Object value,
                                                boolean sel,
                                                boolean expanded, boolean leaf,
                                                int row, boolean hasFocus) {
    super.getTreeCellRendererComponent(tree,value,sel,expanded,leaf,row,hasFocus);
    if (esCara(value)) {
      setIcon(cara);
    }
    else if (esTarget(value)) {
      setIcon(rule);
    }
    else if (esAction(value)) {
      setIcon(verde);
    }
    else if (esNube(value)) {
      setIcon(nube);
    }
    else {

    }
    // JR Set font similar to ArchStudio. The tree cell uses normal font
    setFont(new Font("SansSerif", Font.PLAIN, 12));
    // JREND
    
    return this;
  }

  protected boolean esCara(Object value) {
    DefaultMutableTreeNode node =
        (DefaultMutableTreeNode) value;
    if(!(value instanceof DefaultMutableTreeNode)) return false;
    if(!(node.getUserObject() instanceof ElementoXACML)) return false;
    ElementoXACML st=(ElementoXACML)node.getUserObject();
    if(st.getTipo().equals(ElementoSubjects.TIPO_SUBJECTS) || st.getTipo().equals("Subject")) return true;
    return false;
  }

  protected boolean esAction(Object value) {
    DefaultMutableTreeNode node =
        (DefaultMutableTreeNode) value;
    if(!(value instanceof DefaultMutableTreeNode)) return false;
    if(!(node.getUserObject() instanceof ElementoXACML)) return false;
    ElementoXACML st=(ElementoXACML)node.getUserObject();
    if(st.getTipo().equals(ElementoActions.TIPO_ACTIONS) || st.getTipo().equals(ElementoAction.TIPO_ACTION)) return true;
    return false;
  }

  protected boolean esTarget(Object value) {
    DefaultMutableTreeNode node =
        (DefaultMutableTreeNode) value;

    if(!(value instanceof DefaultMutableTreeNode)) return false;
    if(!(node.getUserObject() instanceof ElementoXACML)) return false;
    ElementoXACML st=(ElementoXACML)node.getUserObject();
    if(st.getTipo().equals(ElementoTarget.TIPO_TARGET)) return true;
    return false;
  }

  protected boolean esNube(Object value) {
    DefaultMutableTreeNode node =
        (DefaultMutableTreeNode) value;

    if(!(value instanceof DefaultMutableTreeNode)) return false;
    if(!(node.getUserObject() instanceof ElementoXACML)) return false;
    ElementoXACML st=(ElementoXACML)node.getUserObject();
    if(st.getTipo().equals(ElementoResources.TIPO_RESOURCES) || st.getTipo().equals(ElementoResource.TIPO_RESOURCE)) return true;
    return false;
  }

}
