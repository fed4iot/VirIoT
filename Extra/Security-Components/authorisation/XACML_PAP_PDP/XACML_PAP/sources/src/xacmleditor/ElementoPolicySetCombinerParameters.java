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

import java.util.Map;

/** This class represents the XACML CombinerParameters Element.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public class ElementoPolicySetCombinerParameters
    extends ElementoXACML{

  public static final String TIPO_POLICYSETCOMBINERPARAMETERS="PolicySetCombinerParameters";

  public ElementoPolicySetCombinerParameters(Map ht) {
    super.setTipo(TIPO_POLICYSETCOMBINERPARAMETERS);
    super.setAtributos(ht);
  }

  public String getID() {
    return (String)super.getAtributos().get("PolicySetIdRef");
  }

  public String toString(){
    String aux="<"+getTipo();
    if(esVacio()) return aux+"/>";
    return aux+">";
  }

  public String[] getAllowedChild(){
     String[] allowedChild={"CombinerParameter"};
     return allowedChild;
  }
  public String[] getAllObligatory() {
    String[] AllObligatory = null;
  return AllObligatory;
  }


}
