/*
 * Copyright 2005, 2006 Alberto Jim�nez L�zaro
 *                      Pablo Galera Morcillo (umu-xacml-editor-admin@dif.um.es)
 *                      Dpto. de Ingenier�a de la Informaci�n y las Comunicaciones
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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;

/* **************************************************************
 * Name: ElementoTarget
 *
 * Description: */
/** This class represents XACML the Target Element.
 *
 * @author Alberto Jim�nez L�zaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public class ElementoTarget
    extends ElementoXACML {

  public static final String TIPO_TARGET="Target";
  private String[] allowedChild={"Subjects","Resources","Actions","Environments"};

  public ElementoTarget(Map ht) {
    super.setTipo(TIPO_TARGET);
    super.setAtributos(ht);
  }

  public String getID(){
    return "";
  }

  public String toString(){
    String aux="<"+getTipo();
    if(esVacio()) return aux+"/>";
    return aux+">";
  }

  public int getPosicion(ElementoXACML e) {
    ArrayList array = new ArrayList(Arrays.asList(allowedChild));
    if(array.contains(e.getTipo())) return array.indexOf(e.getTipo());
    return super.getPosicion(e);
  }

  public String[] getAllowedChild(){
     return allowedChild;
  }

  public String[] getAllObligatory() {
    String[] AllObligatory = null;
  return AllObligatory;
  }

  public int getMaxNumChild(ElementoXACML e) {
    int i;
    // Permitidos son �nicos
    for(i=0;i<getAllowedChild().length;i++){
      if(e.getTipo().equals(getAllowedChild()[i])) return 1;
    }
    return super.getMaxNumChild(e);
  }

}
