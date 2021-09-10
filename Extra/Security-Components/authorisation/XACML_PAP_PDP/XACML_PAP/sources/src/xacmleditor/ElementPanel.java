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
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import java.awt.event.*;
import java.util.Observable;
import java.util.Observer;

/** The superclass of all panels.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public class ElementPanel
    extends JPanel {
  MiObservable miobservable = new MiObservable();
  protected DefaultMutableTreeNode nodo;
  protected ElementoXACML elemento;
  protected DefaultTreeModel dtm;

  public ElementPanel(DefaultMutableTreeNode n) {
    nodo = n;
    elemento = (ElementoXACML) nodo.getUserObject();
  }

  public void setTreeModel(DefaultTreeModel d){
    dtm=d;
  }

  public void addObserver(Observer obs) {
    miobservable.addObserver(obs);
  }

  public void deleteObserver(Observer obs) {
    miobservable.deleteObserver(obs);
  }

  public void keyReleased(KeyEvent e) {}
  public void itemStateChanged(ItemEvent e){}
  public void actionPerformed(ActionEvent e) {}
  public void actualizar(){}
  public void valueChanged(ListSelectionEvent e) {}


}

class MiObservable
    extends Observable {
  public void cambiar() {
    setChanged();
    notifyObservers();
  }

  public void cambiar(Object o) {
    setChanged();
    this.notifyObservers(o);
  }
}

class MiElementActionAdapter
    implements ActionListener {
  private ElementPanel adaptee;

  MiElementActionAdapter(ElementPanel adaptee) {
    this.adaptee = adaptee;
  }

  public void actionPerformed(ActionEvent e) {
    adaptee.actionPerformed(e);
  }
}

class MiElementKeyAdapter
    extends KeyAdapter {
  	private ElementPanel adaptee;

	MiElementKeyAdapter(ElementPanel adaptee) {
	    this.adaptee = adaptee;
  	}

  public void keyReleased(KeyEvent e) {
         adaptee.keyReleased(e);
  }


}


class MiElementItemAdapter
    implements ItemListener {
  private ElementPanel adaptee;

  MiElementItemAdapter(ElementPanel adaptee) {
    this.adaptee = adaptee;
  }

  public void itemStateChanged(ItemEvent e) {
    adaptee.itemStateChanged(e);
  }
}

class MiTreeModelAdapter
    implements TreeModelListener {
  private ElementPanel adaptee;

  MiTreeModelAdapter(ElementPanel adaptee) {
    this.adaptee = adaptee;
  }

  public void treeNodesChanged(TreeModelEvent e) {
  }

  public void treeNodesInserted(TreeModelEvent e) {
    adaptee.actualizar();
  }

  public void treeNodesRemoved(TreeModelEvent e) {
    adaptee.actualizar();
  }

  public void treeStructureChanged(TreeModelEvent e) {
    adaptee.actualizar();
  }
}

class MiListSelectionAdapter
   implements ListSelectionListener {
 private ElementPanel adaptee;
 MiListSelectionAdapter(ElementPanel adaptee) {
   this.adaptee = adaptee;
 }

 public void valueChanged(ListSelectionEvent e) {
   adaptee.valueChanged(e);
 }
   }
