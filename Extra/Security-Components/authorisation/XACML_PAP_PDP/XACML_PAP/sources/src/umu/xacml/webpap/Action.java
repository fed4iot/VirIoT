/*
 *    Copyright (C) 2012, 2013 Universidad de Murcia
 *
 *    Authors:
 *        Ginés Dólera Tormo <ginesdt@um.es>
 *        Juan M. Marín Pérez <juanmanuel@um.es>
 *        Jorge Bernal Bernabé <jorgebernal@um.es>
 *        Gregorio Martínez Pérez <gregorio@um.es>
 *        Antonio F. Skarmeta Gómez <skarmeta@um.es>
 *		  Dan García Carrillo <dan.garcia@um.es>
 *
 *    This file is part of XACML Web Policy Administration Point (XACML-WebPAP).
 *
 *    XACML-WebPAP is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Lesser General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    XACML-WebPAP is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *    GNU Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public License
 *    along with XACML-WebPAP. If not, see <http://www.gnu.org/licenses/>.
 * 
 */
package umu.xacml.webpap;


import Umu_xacml_util.Umu_xacml_util;
import xacmleditor.ElementoAction;
import xacmleditor.ElementoActionAttributeDesignator;
import xacmleditor.ElementoActionMatch;
import xacmleditor.ElementoAttributeValue;

public class Action extends XACMLAttributeElement{

		static public Action ALLSELECTED = new Action();

		public static final String sortingParameter = "action";

		public Action(){
			super();
		}

		public Action(String name, String id){
			super(name,id, sortingParameter);
		}

		
	    /**
	     * Creates a new instance using an action element of the XACML Editor library.
	     * @param umu_xacml_util utility object to be used.
	     * @param elementoAction the action element.
	     */
	    public Action(Umu_xacml_util umu_xacml_util, ElementoAction elementoAction) {
	    	//TODO: FALTA POR HACER EN CADA HEREDERO DE LA CLASE!
	        super (null,null,sortingParameter);

	    	ElementoActionMatch elementoActionMatch = (ElementoActionMatch) umu_xacml_util.getChild(
	                elementoAction,
	                ElementoActionMatch.TIPO_ACTIONMATCH);
	        
	        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.getChild(
	                elementoActionMatch,
	                ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);

	        ElementoActionAttributeDesignator elementoAttributeValueDesignator = (ElementoActionAttributeDesignator) umu_xacml_util.getChild(elementoActionMatch, ElementoActionAttributeDesignator.TIPO_ACTIONATTRIBUTEDESIGNATOR);
	        
	        this.setName((String) elementoAttributeValue.getContenido());
	        this.setXACMLID((String) elementoAttributeValueDesignator.getID());
	    }


	    /**
	     * Returns the utility object for this action.
	     * @return the utility object of the action.
	     */
	    public Umu_xacml_util getUMU_XACML() {
	        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
	        ElementoAction elementoAction = (ElementoAction) umu_xacml_util.createPrincipal(ElementoAction.TIPO_ACTION);
	        ElementoActionMatch elementoActionMatch = (ElementoActionMatch) umu_xacml_util.createChild(elementoAction, ElementoActionMatch.TIPO_ACTIONMATCH);
	        elementoActionMatch.getAtributos().put("MatchId", "urn:oasis:names:tc:xacml:1.0:function:string-equal");

	        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.createChild(elementoActionMatch, ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);
	        elementoAttributeValue.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
	        elementoAttributeValue.setContenido(getName());

	        ElementoActionAttributeDesignator elementoActionAttributeDesignator = (ElementoActionAttributeDesignator) umu_xacml_util.createChild(elementoActionMatch, ElementoActionAttributeDesignator.TIPO_ACTIONATTRIBUTEDESIGNATOR);
	        elementoActionAttributeDesignator.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
	        elementoActionAttributeDesignator.getAtributos().put("AttributeId", getXACMLID());
	        return umu_xacml_util;
	    }

}
