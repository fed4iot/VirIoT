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

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;


import Umu_xacml_util.Umu_xacml_util;
import xacmleditor.ElementoAction;
import xacmleditor.ElementoActionAttributeDesignator;
import xacmleditor.ElementoActionMatch;
import xacmleditor.ElementoAttributeValue;
import xacmleditor.ElementoSubject;
import xacmleditor.ElementoSubjectAttributeDesignator;
import xacmleditor.ElementoSubjectMatch;


/**
 * This class represents an XACML Subject element.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */

public class Subject extends XACMLAttributeElement{
	
    static public Subject ALLSELECTED = new Subject();

	public static final String sortingParameter = "subject";

	public Subject(){
		super();
	}
	
	public Subject(String name,String id){
		super(name,id, sortingParameter);
	}

    /**
     * Creates a new instance using an action element of the XACML Editor library.
     * @param umu_xacml_util utility object to be used.
     * @param elementoAction the action element.
     */
    public Subject(Umu_xacml_util umu_xacml_util, ElementoSubject elementoSubject) {
    	//TODO: FALTA POR HACER EN CADA HEREDERO DE LA CLASE!
        super (null,null,sortingParameter);

    	ElementoSubjectMatch elementoSubjectMatch = (ElementoSubjectMatch) umu_xacml_util.getChild(
    			elementoSubject,
                ElementoSubjectMatch.TIPO_SUBJECTMATCH);
        
        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.getChild(
        		elementoSubjectMatch,
                ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);

        ElementoSubjectAttributeDesignator elementoSubjectValueDesignator = (ElementoSubjectAttributeDesignator) umu_xacml_util.getChild(elementoSubjectMatch, ElementoSubjectAttributeDesignator.TIPO_SUBJECTATTRIBUTEDESIGNATOR);
        
        this.setName((String) elementoAttributeValue.getContenido());
        this.setXACMLID((String) elementoSubjectValueDesignator.getID());
    }

    /**
     * Returns the utility object for this action.
     * @return the utility object of the action.
     */
    public Umu_xacml_util getUMU_XACML() {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
        ElementoSubject elementoSubject = (ElementoSubject) umu_xacml_util.createPrincipal(ElementoSubject.TIPO_SUBJECT);
        ElementoSubjectMatch elementoSubjectMatch = (ElementoSubjectMatch) umu_xacml_util.createChild(elementoSubject, ElementoSubjectMatch.TIPO_SUBJECTMATCH);
        elementoSubjectMatch.getAtributos().put("MatchId", "urn:oasis:names:tc:xacml:1.0:function:string-equal");

        ElementoAttributeValue elementoAttributeValue = (ElementoAttributeValue) umu_xacml_util.createChild(elementoSubjectMatch, ElementoAttributeValue.TIPO_ATTRIBUTEVALUE);
        elementoAttributeValue.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
        elementoAttributeValue.setContenido(getName());

        ElementoSubjectAttributeDesignator elementoSubjectAttributeDesignator = (ElementoSubjectAttributeDesignator) umu_xacml_util.createChild(elementoSubjectMatch, ElementoSubjectAttributeDesignator.TIPO_SUBJECTATTRIBUTEDESIGNATOR);
        elementoSubjectAttributeDesignator.getAtributos().put("DataType", "http://www.w3.org/2001/XMLSchema#string");
        elementoSubjectAttributeDesignator.getAtributos().put("AttributeId", getXACMLID());
        return umu_xacml_util;
    }


	
}