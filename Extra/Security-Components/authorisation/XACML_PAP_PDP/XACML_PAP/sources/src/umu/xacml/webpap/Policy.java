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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import xacmleditor.ElementoObligation;
import xacmleditor.ElementoObligations;
import xacmleditor.ElementoPolicy;
import xacmleditor.ElementoRule;
import xacmleditor.ElementoTarget;

/**
 * This class represents an XACML Policy element.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class Policy implements NamedObject{

    // rules, are the persistent rules,
	// changingRules are the GUI changed Rules, susceptible to be saved, replacing rules. 
	private HashMap<String,Rule> rules;
	private List<Rule> ruleList;
    
	private String combiningAlg;
    private String policyId;
    private List<Obligation> obligations;

    /**
     * Creates a new policy.
     */
    public Policy() {
        rules = new HashMap<String,Rule>();
        ruleList = new ArrayList<Rule>();
        combiningAlg = null;
        policyId = null;
    }

    public Policy(String policyId){
    	
    	this.policyId = policyId;
    	this.combiningAlg = "urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:first-applicable";
    	this.rules = new HashMap<String,Rule>();
        this.ruleList = new ArrayList<Rule>();
    }
    
    /**
     * Creates a new instance using a policy element of the XACML Editor library.
     * @param umu_xacml_util umu_xacml_util utility object to be used.
     * @param elementoPolicy the policy element.
     */
    public Policy(Umu_xacml_util umu_xacml_util, ElementoPolicy elementoPolicy) {
        this.combiningAlg = (String) elementoPolicy.getAtributos().get("RuleCombiningAlgId");
        this.policyId = (String) elementoPolicy.getAtributos().get("PolicyId");

        rules = new HashMap<String,Rule>();
        ruleList = new ArrayList<Rule>();
        List elementoRules = umu_xacml_util.getChildren(elementoPolicy, ElementoRule.TIPO_RULE);
        Iterator it = elementoRules.iterator();
        while (it.hasNext()) {
            ElementoRule elementoRule = (ElementoRule) it.next();
            Rule rule = new Rule(umu_xacml_util, elementoRule);
            rules.put(rule.getKeyForMap(),rule);
            ruleList.add(rule);
        }

        ElementoObligations elementoObligations = (ElementoObligations) umu_xacml_util.getChild(elementoPolicy, ElementoObligations.TIPO_OBLIGATIONS);
        if (elementoObligations != null) {
            obligations = new ArrayList<Obligation>();
            List elementosObligation = umu_xacml_util.getChildren(elementoObligations, ElementoObligation.TIPO_OBLIGATION);
            Iterator it2 = elementosObligation.iterator();
            while (it2.hasNext()) {
                ElementoObligation elementoObligation = (ElementoObligation) it2.next();
                Obligation obligation = new Obligation(umu_xacml_util, elementoObligation);
                obligations.add(obligation);
            }
        }
    }

    /**
     * Returns the id of the policy.
     * @return the id of the policy.
     */
    public String getPolicyId() {
        return policyId;
    }
    
    public String getName(){
    	return this.getPolicyId();
    }

    /**
     * Sets the id of the policy.
     * @param policyId the id of the policy.
     */
    public void setPolicyId(String policyId) {
        this.policyId = policyId;
    }

    /**
     * Returns the combining algorithm of the policy.
     * @return the combining algorithm of the policy.
     */
    public String getCombiningAlg() {
        return combiningAlg;
    }

    /**
     * Sets the combining algorithm of the policy.
     * @param combiningAlg the combining algorithm of the policy.
     */
    public void setCombiningAlg(String combiningAlg) {
        this.combiningAlg = combiningAlg;
    }

    /**
     * Returns the rules of the policy.
     * @return the rules of the policy.
     */
    public List<Rule> getRules() {
/*    	List<Rule> ruleList = new ArrayList<Rule>();
    	for(Entry <String,Rule>rule : rules.entrySet())
    		ruleList.add(rule.getValue());*/
    	return ruleList;
    }

    public Map<String,Rule> getRulesMap(){
    	return this.rules;
    }
    /**
     * Sets the rules of the policy.
     * @param rules the rules of the policy.
     */
    public void setRules(List<Rule> rules) {
		this.ruleList = rules;
    }
    
    public void setRules(Map<String,Rule> rules){
    	this.rules = new HashMap<String,Rule>(rules);
    }

    public void deleteRuleByName(String name){
    	for (int i = 0; i < this.ruleList.size(); i++)
			if(this.ruleList.get(i).getName().equals(name)){
				this.ruleList.remove(i);
				return;
			}
    }

    public Rule getRuleByName(String name){
    	for (int i = 0; i < this.ruleList.size(); i++)
			if(this.ruleList.get(i).getName().equals(name)){
				return this.ruleList.get(i);
			}
    	return null;
    }

    
    /**
     * Returns the utility object for this policy.
     * @return the utility object for this policy.
     */
    public Umu_xacml_util getUMU_XACML() {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
        ElementoPolicy elementoPolicy = (ElementoPolicy) umu_xacml_util.createPrincipal(ElementoPolicy.TIPO_POLICY);
   
        elementoPolicy.getAtributos().put("PolicyId", policyId);
        elementoPolicy.getAtributos().put("RuleCombiningAlgId", combiningAlg);
        umu_xacml_util.createChild(elementoPolicy, ElementoTarget.TIPO_TARGET);

        Iterator<Rule> rulesIt = getRules().iterator();
        while (rulesIt.hasNext()) {
            Rule rule = rulesIt.next();
            umu_xacml_util.insertChild(elementoPolicy, rule.getUMU_XACML());
        }

        if (obligations != null) {
            ElementoObligations elementoObligations = (ElementoObligations) umu_xacml_util.createChild(elementoPolicy, ElementoObligations.TIPO_OBLIGATIONS);
            Iterator<Obligation> obligationIt = obligations.iterator();
            while (obligationIt.hasNext()) {
                Obligation obligation = obligationIt.next();
                umu_xacml_util.insertChild(elementoObligations, obligation.getUMU_XACML());
            }
        }

        return umu_xacml_util;
    }

    /**
     * Returns a string representation of the policy.
     * @return string representation of the policy.
     */
    @Override
    public String toString() {
    	// TODO: tostring changed.
    	return this.getClass().getName() + "["+ this.getName()+"]";
    	//        return getUMU_XACML().toString();
    }

    /**
     * Returns the obligations of the policy.
     * @return the obligations of the policy.
     */
    public List<Obligation> getObligations() {
        return obligations;
    }

    /**
     * Sets the obligations of the policy.
     * @param obligations the obligations of the policy.
     */
    public void setObligations(List<Obligation> obligations) {
        this.obligations = obligations;
    }

	@Override
	public String getKeyForMap() {
		// TODO Auto-generated method stub
		return null;
	}
}
