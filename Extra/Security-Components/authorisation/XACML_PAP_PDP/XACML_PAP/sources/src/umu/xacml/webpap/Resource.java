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
import xacmleditor.ElementoAttributeValue;
import xacmleditor.ElementoResource;
import xacmleditor.ElementoResourceAttributeDesignator;
import xacmleditor.ElementoResourceMatch;

public class Resource extends XACMLAttributeElement{
	
    static public Resource ALLSELECTED = new Resource();
	
	public static final String sortingParameter = "resource";

	public Resource(){
		super();
	}

	public Resource(String name,String id){
		super(name,id, sortingParameter);
	}
	
	
    /**
     * Creates a new instance using an action element of the XACML Editor library.
     * @param umu_xacml_util utility object to be used.
     * @param elementoAction the action element.
     */
    public Resource(Umu_xacml_util umu_xacml_util, ElementoResource elementoResource) {
    	//TODO: FALTA POR HACER EN CADA HEREDERO DE LA CLASE!
        super (null,null,sortingParameter);

    	ElementoResourceMatch elementoResourceMatch = (ElementoResourceMatch) umu_xacml_util.getChild(
    			elementoResource,
                ElementoResourceMatch.TIPO_RESOURCEMATCH);
        
        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.getChild(
                elementoResourceMatch,
                ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);

        ElementoResourceAttributeDesignator elementoResourceValueDesignator = (ElementoResourceAttributeDesignator) umu_xacml_util.getChild(elementoResourceMatch,ElementoResourceAttributeDesignator.TIPO_RESOURCEATTRIBUTEDESIGNATOR);
        
        this.setName((String) elementoAttributeValue.getContenido());
        this.setXACMLID((String) elementoResourceValueDesignator.getID());
    }


    /**
     * Returns the utility object for this action.
     * @return the utility object of the action.
     */
    public Umu_xacml_util getUMU_XACML() {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
        ElementoResource elementoResource = (ElementoResource) umu_xacml_util.createPrincipal(ElementoResource.TIPO_RESOURCE);
        ElementoResourceMatch elementoResourceMatch = (ElementoResourceMatch) umu_xacml_util.createChild(elementoResource, ElementoResourceMatch.TIPO_RESOURCEMATCH);
        elementoResourceMatch.getAtributos().put("MatchId", "urn:oasis:names:tc:xacml:1.0:function:string-equal");

        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.createChild(elementoResourceMatch, ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);
        elementoAttributeValue.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
        elementoAttributeValue.setContenido(getName());

        ElementoResourceAttributeDesignator elementoResourceAttributeDesignator = (ElementoResourceAttributeDesignator) umu_xacml_util.createChild(elementoResourceMatch, ElementoResourceAttributeDesignator.TIPO_RESOURCEATTRIBUTEDESIGNATOR);
        elementoResourceAttributeDesignator.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
        elementoResourceAttributeDesignator.getAtributos().put("AttributeId", getXACMLID());
        return umu_xacml_util;
    }

    
}