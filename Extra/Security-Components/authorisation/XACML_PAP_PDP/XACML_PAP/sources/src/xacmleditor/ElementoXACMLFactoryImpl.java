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


/**Implementation of the ElementoXACMLFactory. This class is a Singleton.
 *
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class ElementoXACMLFactoryImpl implements ElementoXACMLFactory{

  protected static ElementoXACMLFactory instancia=new ElementoXACMLFactoryImpl();

  private ElementoXACMLFactoryImpl(){
  }

  public ElementoXACML obtenerElementoXACML(String tipo,Map atributos){
    ElementoXACML elem=null;
    if(tipo.equals(ElementoPolicySet.TIPO_POLICYSET)){
      elem=new ElementoPolicySet(atributos);
    }
    if(tipo.equals(ElementoPolicySetDefaults.TIPO_POLICYSETDEFAULTS)){
      elem=new ElementoPolicySetDefaults(atributos);
    }
    if(tipo.equals(ElementoXPathVersion.TIPO_XPATHVERSION)){
      elem=new ElementoXPathVersion(atributos);
    }
    else if(tipo.equals(ElementoPolicy.TIPO_POLICY)){
      elem=new ElementoPolicy(atributos);
    }
    else if(tipo.equals(ElementoVariableDefinition.TIPO_VARIABLEDEFINITION)){
      elem=new ElementoVariableDefinition(atributos);
    }
    if(tipo.equals(ElementoPolicyDefaults.TIPO_POLICYDEFAULTS)){
      elem=new ElementoPolicyDefaults(atributos);
    }
    else if(tipo.equals(ElementoRule.TIPO_RULE)){
      elem=new ElementoRule(atributos);
    }
    else if(tipo.equals(ElementoTarget.TIPO_TARGET)){
      elem=new ElementoTarget(atributos);
    }
    else if(tipo.equals(ElementoSubjects.TIPO_SUBJECTS)){
      elem=new ElementoSubjects(atributos);
    }
    else if(tipo.equals(ElementoActions.TIPO_ACTIONS)){
      elem=new ElementoActions(atributos);
    }
    else if(tipo.equals(ElementoResources.TIPO_RESOURCES)){
      elem=new ElementoResources(atributos);
    }
    // JR
    else if(tipo.equals(ElementoAnySubject.TIPO_ANY_SUBJECT)){
        elem=new ElementoAnySubject(atributos);
      }
      else if(tipo.equals(ElementoAnyAction.TIPO_ANY_ACTION)){
        elem=new ElementoAnyAction(atributos);
      }
      else if(tipo.equals(ElementoAnyResource.TIPO_ANY_RESOURCE)){
        elem=new ElementoAnyResource(atributos);
      }
    // JREND
    else if(tipo.equals(ElementoEnvironments.TIPO_ENVIRONMENTS)){
      elem=new ElementoEnvironments(atributos);
    }
    else if(tipo.equals(ElementoAttributeValue.TIPO_ATTRIBUTEVALUE )){
      elem=new ElementoAttributeValue(atributos);
    }
    else if(tipo.equals(ElementoAction.TIPO_ACTION)){
      elem=new ElementoAction(atributos);
    }
    else if(tipo.equals(ElementoActionMatch.TIPO_ACTIONMATCH)){
      elem=new ElementoActionMatch(atributos);
    }
    else if(tipo.equals(ElementoActionAttributeDesignator.TIPO_ACTIONATTRIBUTEDESIGNATOR )){
      elem=new ElementoActionAttributeDesignator(atributos);
    }
    else if(tipo.equals(ElementoAttributeSelector.TIPO_ATTRIBUTESELECTOR)){
      elem=new ElementoAttributeSelector(atributos);
    }
    else if(tipo.equals(ElementoSubject.TIPO_SUBJECT)){
      elem=new ElementoSubject(atributos);
    }
    else if(tipo.equals(ElementoSubjectMatch.TIPO_SUBJECTMATCH)){
      elem=new ElementoSubjectMatch(atributos);
    }
    else if(tipo.equals(ElementoSubjectAttributeDesignator.TIPO_SUBJECTATTRIBUTEDESIGNATOR)){
      elem=new ElementoSubjectAttributeDesignator(atributos);
    }

    else if(tipo.equals(ElementoResource.TIPO_RESOURCE)){
      elem=new ElementoResource(atributos);
    }
    else if(tipo.equals(ElementoResourceMatch.TIPO_RESOURCEMATCH)){
      elem=new ElementoResourceMatch(atributos);
    }
    else if(tipo.equals(ElementoResourceAttributeDesignator.TIPO_RESOURCEATTRIBUTEDESIGNATOR)){
      elem=new ElementoResourceAttributeDesignator(atributos);
    }
    else if(tipo.equals(ElementoEnvironment.TIPO_ENVIRONMENT)){
      elem=new ElementoEnvironment(atributos);
    }
    else if(tipo.equals(ElementoEnvironmentMatch.TIPO_ENVIRONMENTMATCH)){
      elem=new ElementoEnvironmentMatch(atributos);
    }
    else if(tipo.equals(ElementoEnvironmentAttributeDesignator.TIPO_ENVIRONMENTATTRIBUTEDESIGNATOR)){
      elem=new ElementoEnvironmentAttributeDesignator(atributos);
    }
    else if(tipo.equals(ElementoCondition.TIPO_CONDITION)){
      elem=new ElementoCondition(atributos);
    }
    else if(tipo.equals(ElementoApply.TIPO_APPLY)){
      elem=new ElementoApply(atributos);
    }
    else if(tipo.equals(ElementoDescription.TIPO_DESCRIPTION)){
      elem=new ElementoDescription(atributos);
    }
    else if(tipo.equals(ElementoObligations.TIPO_OBLIGATIONS)){
      elem=new ElementoObligations(atributos);
    }
    else if(tipo.equals(ElementoObligation.TIPO_OBLIGATION)){
      elem=new ElementoObligation(atributos);
    }
    else if(tipo.equals(ElementoAttributeAssignment.TIPO_ATTRIBUTEASSIGNMENT)){
      elem=new ElementoAttributeAssignment(atributos);
    }
    else if(tipo.equals(ElementoCombinerParameters.TIPO_COMBINERPARAMETERS)){
      elem=new ElementoCombinerParameters(atributos);
    }
    else if(tipo.equals(ElementoCombinerParameter.TIPO_COMBINERPARAMETER)){
      elem=new ElementoCombinerParameter(atributos);
    }
    else if(tipo.equals(ElementoRuleCombinerParameters.TIPO_RULECOMBINERPARAMETERS)){
      elem=new ElementoRuleCombinerParameters(atributos);
    }
    else if(tipo.equals(ElementoPolicyCombinerParameters.TIPO_POLICYCOMBINERPARAMETERS)){
      elem=new ElementoPolicyCombinerParameters(atributos);
    }
    else if(tipo.equals(ElementoPolicySetCombinerParameters.TIPO_POLICYSETCOMBINERPARAMETERS)){
      elem=new ElementoPolicySetCombinerParameters(atributos);
    }
    else if(tipo.equals(ElementoFunction.TIPO_FUNCTION)){
      elem=new ElementoFunction(atributos);
    }
    else if(tipo.equals(ElementoVariableReference.TIPO_VARIABLEREFERENCE)){
      elem=new ElementoVariableReference(atributos);
    }
    else if(tipo.equals(ElementoPolicySetIdReference.TIPO_POLICYSETIDREFERENCE)){
      elem=new ElementoPolicySetIdReference(atributos);
    }
    else if(tipo.equals(ElementoPolicyIdReference.TIPO_POLICYIDREFERENCE)){
      elem=new ElementoPolicyIdReference(atributos);
    }

    return elem;
  }

  public static ElementoXACMLFactory getInstance(){
    return instancia;
  }


}
