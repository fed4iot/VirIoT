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

/** An implementation of XACMLPanelFactory. This class is a singleton.
 *
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class XACMLPanelFactoryImpl
    implements XACMLPanelFactory {

  protected static XACMLPanelFactoryImpl instancia = new XACMLPanelFactoryImpl();

  private XACMLPanelFactoryImpl() {
  }

  public ElementPanel obtenerPanel(DefaultMutableTreeNode n) {
    ElementPanel ret = null;
    if(n==null) return ret;
    if (n.getUserObject() instanceof ElementoMatch) {
      ret = new MatchPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoAttributeValue) {
      ret = new AttributeValuePanel(n);
    }
    else if (n.getUserObject() instanceof ElementoAction) {
      ret = new ListaPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoResource) {
      ret = new ListaPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoSubject) {
      ret = new ListaPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoAttributeDesignator) {
      ret = new AttributeDesignatorPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoAttributeSelector) {
      ret = new AttributeSelectorPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoAttributeAssignment) {
      ret = new AttributeAssignmentPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoRule) {
      ret = new RulePanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicy) {
      ret = new PolicyPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicySet) {
      ret = new PolicySetPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicySetDefaults) {
      ret = new DefaultsPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicyDefaults) {
      ret = new DefaultsPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoVariableDefinition) {
      ret = new VariableDefinitionPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoApply) {
      ret = new ApplyPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoCondition) {
      ret = new ConditionPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoFunction) {
      ret = new FunctionPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoVariableReference) {
      ret = new VariableReferencePanel(n);
    }
    else if (n.getUserObject() instanceof ElementoObligation) {
      ret = new ObligationPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoCombinerParameters) {
      ret = new CombinerParametersPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoRuleCombinerParameters) {
      ret = new CombinerParametersPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicyCombinerParameters) {
      ret = new CombinerParametersPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicySetCombinerParameters) {
      ret = new CombinerParametersPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoCombinerParameter) {
      ret = new CombinerParameterPanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicySetIdReference) {
      ret = new ReferencePanel(n);
    }
    else if (n.getUserObject() instanceof ElementoPolicyIdReference) {
      ret = new ReferencePanel(n);
    }

    return ret;
  }

  public static XACMLPanelFactoryImpl getInstance() {
    return instancia;
  }

}
