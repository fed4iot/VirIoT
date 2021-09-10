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

import javax.swing.tree.DefaultMutableTreeNode;
import java.util.Enumeration;


/**
 * This class permits insert diferentes nodes on the Tree in the correct order
 *
 * @author Alberto Jiménez Lázaro,Pablo Galera Morcillo
 * @version 1.3
 */

public class InsertarOrdenadoElemento {
  protected DefaultMutableTreeNode nodoPadre;
  protected DefaultMutableTreeNode nodoHijo;
  protected ElementoXACML elem;
  ElementoXACML array[];

  public InsertarOrdenadoElemento(DefaultMutableTreeNode nodoPadre,
                                  DefaultMutableTreeNode nodoHijo) {
    this.nodoPadre = nodoPadre;
    this.nodoHijo = nodoHijo;
    elem = (ElementoXACML) nodoPadre.getUserObject();
    array= new ElementoXACML[nodoPadre.getChildCount()+1];
  }

  private int buscarPosicion(int tamano, ElementoXACML elemNum) {
    int posicion = -1;
    for (int i = 0; i < tamano; i++) {
      if (posicion == -1) {
        if (elem.getPosicion(array[i]) > elem.getPosicion(elemNum)) {
          posicion = i;
        }
      }
    }
    return posicion;
  }

  private void moverHaciaLaDerecha(int desde, int hasta) {
    for (int i = hasta; i > desde; i--) {
      array[i] = array[i - 1];
    }
  }

  public void ordenarInsercion() {
    int posicion;
    ElementoXACML elemNum;
    Enumeration hijos = nodoPadre.children();
    int i = 0;

    while (hijos.hasMoreElements()) {
      DefaultMutableTreeNode nodoHijo = (DefaultMutableTreeNode) hijos.
          nextElement();
      array[i] = (ElementoXACML) nodoHijo.getUserObject();
      i++;
    }
    array[i]=(ElementoXACML) nodoHijo.getUserObject();

    for (i = 1; i < array.length; i++) {
      elemNum = array[i];
      posicion = buscarPosicion(i, elemNum);
      if (posicion != -1) {
        moverHaciaLaDerecha(posicion, i);
        array[posicion] = elemNum;
      }
    }
  }

  public int getPosicion(){
    int i;
    for (i = 0; i < array.length; i++) {
      if (array[i].equals( (ElementoXACML) nodoHijo.getUserObject()))return i;
    }
    return i;
  }
}
