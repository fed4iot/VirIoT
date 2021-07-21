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

import java.util.TreeMap;
import java.util.Map.Entry;

/**
 * This class represents an XACML Action element.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class XACMLAttributeElement implements Listable, NamedObject{

    /**
     * Action that represents all available actions.
     */
    static public XACMLAttributeElement ALLSELECTED = new XACMLAttributeElement();
    private String name;

    // TODO: TO BE IMPLEMENTED; FOR NOW IS ALWAYS STRING
    private String dataType;
    private String xacml_id;
    private String sortedValue;
    
    
    //private LinkedHashMap<String,String> ActionAttributes = null;
    
    /**
     * Creates a new action with the given name.
     * @param name the name of the action.
     */
    
    public XACMLAttributeElement(){
    	this.name = "";
        this.xacml_id = "";
    }
    
    public XACMLAttributeElement(String name) {
        this.name = name;
    }

    public XACMLAttributeElement(String name, String xacml_id) {
        this.name = name;
        this.xacml_id = xacml_id;
    }

    public XACMLAttributeElement(String name, String xacml_id,String sortedValue) {
        this.name = name;
        this.xacml_id = xacml_id;
        this.sortedValue = sortedValue;
    }

    /**
     * Returns the name of the action.
     * @return the name of the action.
     */
    public String getName() {
        return name;
    }

    public String getXACMLID(){
    	return xacml_id;
    }
    
    public String getSortedValue() {
        return this.sortedValue;
    }

    public String getKeyForMap(){
    	return this.getName()+" <()> "+this.getXACMLID();
    }
    

    /**
     * Sets the name of the action.
     * @param name the name of the action.
     */
    public void setName(String name) {
        this.name = name;
    }

    public void setXACMLID(String xacml_id) {
        this.xacml_id = xacml_id;
    }

        
    public void setSortedValue(String sortedValue) {
        this.sortedValue= sortedValue;
    }



    /**
     * Returns a string representation of the action.
     * @return string representation of the action.
     */
    @Override
    public String toString() {
        return this.getClass().getName() +": [ name: " + name + ", xacml_id: " + xacml_id +", sortedValue: "+ sortedValue + " ]";
    }

    /**
     * Returns a hash code value for the action.
     * @return hash code value for the action.
     */
    @Override
    public int hashCode() {
        return name.hashCode();
    }

    /**
     * Indicates whether some other object is "equal to" this action.
     * @param obj the reference object with which to compare.
     * @return true if this action equals the argument; false otherwise.
     */
    @Override
    public boolean equals(Object obj) {
    	if(obj == null) return false;
    	return 	 this.toString().equals(obj.toString());
    }

	@Override
	public Entry<String, String> getListableMessage() {
		TreeMap<String,String> toreturn = new TreeMap<String,String>();
		toreturn.put(xacml_id, name);
		return toreturn.firstEntry();
	}
}
