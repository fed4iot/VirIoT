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

/** This class represents the XACML PolicySet Element.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 ****************************************************************/
public class ElementoPolicySet
    extends ElementoXACML {

  public static final String TIPO_POLICYSET = "PolicySet";

  public ElementoPolicySet(Map ht) {
    super.setTipo(TIPO_POLICYSET);
    super.setAtributos(ht);
  }

  public String getID() {
    return (String)super.getAtributos().get("PolicySetId");
  }

  public String[] getAllowedChild() {
	String[] allowedChild = {
        "Description",
        "PolicySetDefaults",
        "Target",
        "PolicySet",
        "Policy",
        "PolicySetIdReference",
        "PolicyIdReference",
        "Obligations",
        "CombinerParameters",
        "PolicySetCombinerParameters",
        "PolicyCombinerParameters"
    };
    return allowedChild;
  }

  public int getPosicion(ElementoXACML e) {
    if(e.getTipo().equals("Description")) return 1;
    else if(e.getTipo().equals("PolicySetDefaults")) return 2;
    if(e.getTipo().equals("Target")) return 3;
    else if(e.getTipo().equals("PolicySet")) return 4;
    else if(e.getTipo().equals("Policy")) return 4;
    else if(e.getTipo().equals("PolicySetIdReference")) return 4;
    else if(e.getTipo().equals("PolicyIdReference")) return 4;
    else if(e.getTipo().equals("CombinerParameters")) return 4;
    else if(e.getTipo().equals("PolicySetCombinerParameters")) return 4;
    else if(e.getTipo().equals("PolicyCombinerParameters")) return 4;
    else if(e.getTipo().equals("Obligations")) return 5;
    return super.getPosicion(e);
  }

  public String[] getAllObligatory() {
    String[] AllObligatory = {
        "Target"
    };
    return AllObligatory;
  }

  public int getMaxNumChild(ElementoXACML e) {
    if(e.getTipo().equals("Target")) return 1;
    else if(e.getTipo().equals("Description")) return 1;
    else if(e.getTipo().equals("PolicySetDefaults")) return 1;
    else if(e.getTipo().equals("Obligations")) return 1;
    else if(e.getTipo().equals("CombinerParameters")) return 1;
    else if(e.getTipo().equals("PolicySetCombinerParameters")) return 1;
    else if(e.getTipo().equals("PolicyCombinerParameters")) return 1;
    return super.getMaxNumChild(e);
  }

}
