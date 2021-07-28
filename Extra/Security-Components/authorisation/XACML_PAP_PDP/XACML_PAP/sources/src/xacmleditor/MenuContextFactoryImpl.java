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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Enumeration;
import java.util.Iterator;



/**
 * This class are implemented according the Singleton pattern. And implements
 * the MenuContextFactory Interface
 *
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 * @version 1.3
 */
public class MenuContextFactoryImpl
    implements MenuContextFactory {

  JPopupMenu menu;
  JMenuItem jmnuPolicySet;
  JMenuItem jmnuPolicy;
  JMenuItem jmnuPolicySetIdReference;
  JMenuItem jmnuPolicyIdReference;
  JMenuItem jmnuRemove;
  JMenuItem jmnuAddResources;
  JMenuItem jmnuAddActions;
  JMenuItem jmnuAddSubjects;
  JMenuItem jmnuAddEnvironments;
  JMenuItem jmnuAddResource;
  JMenuItem jmnuAddAction;
  JMenuItem jmnuAddSubject;
  JMenuItem jmnuAddEnvironment;
  JMenuItem jmnuAddRule;
  JMenuItem jmnuAddCondition;
  JMenuItem jmnuAddAtributeValue;
  JMenuItem jmnuAddApply;
  JMenuItem jmnuAddEnvAttributeDesignator;
  JMenuItem jmnuAddObligation;

  protected static MenuContextFactory instancia = new MenuContextFactoryImpl();

  private MenuContextFactoryImpl() {
    try {
      jbInit();
    }
    catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  public JPopupMenu obtenerMenuContext(DefaultMutableTreeNode n) {
    menu = new JPopupMenu();
    if (n.getUserObject().equals("Policy Document")) {

      JMenuItem jmpaste = menu.add(new JMenuItem("Paste"));
      menu.addSeparator();
      if (n.getChildCount() == 0) {
        jmnuPolicySet = new JMenuItem("add PolicySet");
        jmnuPolicy = new JMenuItem("add Policy");
        menu.add(jmnuPolicySet);
        menu.add(jmnuPolicy);
      }
      if (CurrentCopia.getInstancia().getCurrNode() != null) {
        ElementoXACML eaux = (ElementoXACML) CurrentCopia.getInstancia().
            getCurrNode().getUserObject();
        if (n.getChildCount() == 0) {
          jmpaste.setEnabled(true);
        }
        else {
          String tipo = eaux.getTipo();
          Enumeration children = n.children();
          while (children.hasMoreElements()) {
            DefaultMutableTreeNode nodoHijo = (DefaultMutableTreeNode) children.
                nextElement();
            if (nodoHijo.getUserObject().getClass().getName().equals("xacmleditor.Elemento" +
                tipo)) {
              jmpaste.setEnabled(true);
            }
            else {
              jmpaste.setEnabled(false);
            }
          }
        }
      }
      else {
        jmpaste.setEnabled(false);
      }
    }
    else {
      ElementoXACML elem = (ElementoXACML) n.getUserObject();

      ElementoXACML padre = null;
      try {
        padre = (ElementoXACML) ( (DefaultMutableTreeNode) n.
                                 getParent()).getUserObject();
      }
      catch (ClassCastException exc) {
      }

      menu.add(new JMenuItem("Copy"));
      JMenuItem jmpaste = menu.add(new JMenuItem("Paste"));
      if (CurrentCopia.getInstancia().getCurrNode() != null) {
        ElementoXACML eaux = (ElementoXACML) CurrentCopia.getInstancia().
            getCurrNode().getUserObject();
        if ( ( (ElementoXACML) elem).isAllowedChild(eaux)) {
          jmpaste.setEnabled(true);
        }
        else {
          jmpaste.setEnabled(false);
        }

      }
      else {
        jmpaste.setEnabled(false);
      }

      menu.addSeparator();

      // Menu eliminar

      if (padre != null) {
        Enumeration hijos = n.getParent().children();
        // Contamos cuantos hay como el elemento
        // para saber si lo podemos eleminar
        int num = 0;
        while (hijos.hasMoreElements()) {
          DefaultMutableTreeNode nodoHijo = (DefaultMutableTreeNode) hijos.
              nextElement();
          ElementoXACML elemHijo = (ElementoXACML) nodoHijo.getUserObject();
          if (elemHijo.getTipo().equals(elem.getTipo())) {
            num++;
          }
        }

        if (padre.getMinNumChild(elem) < num) {
          jmnuRemove = new JMenuItem("remove " + elem.getTipo());
          menu.add(jmnuRemove);
        }
      }
      else {
        jmnuRemove = new JMenuItem("remove " + elem.getTipo());
        menu.add(jmnuRemove);
      }

      // Menu agregar

      String permitidos[] = elem.getAllowedChild();
      if (permitidos != null) {
        Enumeration hijos = n.children();
        ArrayList arrayPermitidos = new ArrayList(Arrays.asList(permitidos));
        while (hijos.hasMoreElements()) {
          DefaultMutableTreeNode nodoHijo = (DefaultMutableTreeNode) hijos.
              nextElement();
          ElementoXACML elemHijo = (ElementoXACML) nodoHijo.getUserObject();
          if (elem.getMaxNumChild(elemHijo) == 1) {
            arrayPermitidos.remove(elemHijo.getTipo());
          }
        }
        Iterator it = arrayPermitidos.iterator();
        JMenuItem auxi;
        while (it.hasNext()) {
          auxi = new JMenuItem("add " + (String) it.next());
          menu.add(auxi);
        }
      }
    }
    return menu;
  }

  public static MenuContextFactory getInstance() {
    return instancia;
  }

  private void jbInit() throws Exception {
  }

}
