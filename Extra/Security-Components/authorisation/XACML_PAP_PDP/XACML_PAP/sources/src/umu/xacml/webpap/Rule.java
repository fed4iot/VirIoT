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

import xacmleditor.ElementoAction;
import xacmleditor.ElementoActions;
import xacmleditor.ElementoResource;
import xacmleditor.ElementoResources;
import xacmleditor.ElementoRule;
import xacmleditor.ElementoSubject;
import xacmleditor.ElementoSubjects;
import xacmleditor.ElementoTarget;

/**
 * This class represents an XACML Rule element.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class Rule implements NamedObject{

    private String name;
    private List<Resource> resources;
    private List<Subject> subjects;
    private String policy;
    private List<Action> actions;

    /**
     * Permit value of a rule.
     */
    static public String RULE_PERMIT = "Permit";
    /**
     * Deny value of a rule.
     */
    static public String RULE_DENY = "Deny";
    /**
     * Read action of a rule.
     */
    static public String ACTION_READ = "Read";
    /**
     * Write action of a rule.
     */
    static public String ACTION_WRITE = "Write";

    /**
     * Creates a new rule with the given name.
     * @param name the name of the rule.
     */
    public Rule(String name) {
        resources 	= new ArrayList<Resource>();
        subjects 	= new ArrayList<Subject>();
        actions 	= new ArrayList<Action>();
        policy 		= RULE_PERMIT;

        this.name 	= name;
    }

    /**
     * Creates a new instance using a rule element of the XACML Editor library.
     * @param umu_xacml_util utility object to be used.
     * @param elementoRule the rule element.
     */
    public Rule(Umu_xacml_util umu_xacml_util, ElementoRule elementoRule) {
        name = (String) elementoRule.getAtributos().get("RuleId");
        policy = (String) elementoRule.getAtributos().get("Effect");
        ElementoTarget elementoTarget = (ElementoTarget) umu_xacml_util.getChild(elementoRule, ElementoTarget.TIPO_TARGET);
        resources = new ArrayList<Resource>();

        ElementoResources elementoResources = (ElementoResources) umu_xacml_util.getChild(elementoTarget,
                ElementoResources.TIPO_RESOURCES);
        if (elementoResources == null) {
            resources.add((Resource) Resource.ALLSELECTED);
        } else {

            Iterator it = umu_xacml_util.getChildren(elementoResources, ElementoResource.TIPO_RESOURCE).iterator();
            while (it.hasNext()) {
                ElementoResource elementoResource = (ElementoResource) it.next();

                Resource resource = new Resource(umu_xacml_util, elementoResource);
                resources.add(resource);
            }
        }

        subjects = new ArrayList<Subject>();
        ElementoSubjects elementoSubjects = (ElementoSubjects) umu_xacml_util.getChild(elementoTarget,
                ElementoSubjects.TIPO_SUBJECTS);
        if (elementoSubjects == null) {
            subjects.add((Subject) Subject.ALLSELECTED);
        } else {
            Iterator it = umu_xacml_util.getChildren(elementoSubjects, ElementoSubject.TIPO_SUBJECT).iterator();
            while (it.hasNext()) {
                ElementoSubject elementoSubject = (ElementoSubject) it.next();
                XACMLAttributeElement subject = new Subject(umu_xacml_util, elementoSubject);
                subjects.add((Subject) subject);
            }
        }

        actions = new ArrayList<Action>();
        ElementoActions elementoActions = (ElementoActions) umu_xacml_util.getChild(elementoTarget, ElementoActions.TIPO_ACTIONS);
        if (elementoActions == null) {
            actions.add((Action) Action.ALLSELECTED);
        } else {
            Iterator it = umu_xacml_util.getChildren(elementoActions, ElementoAction.TIPO_ACTION).iterator();
            while (it.hasNext()) {
                ElementoAction elementoAction = (ElementoAction) it.next();
                XACMLAttributeElement action = new Action(umu_xacml_util, elementoAction);
                actions.add((Action) action);
            }
        }
    }

    /**
     * Returns the name of the rule.
     * @return the name of the rule.
     */
    public String getName() {
        return name;
    }

    public String getKeyForMap(){
    	return this.getName();
    }
    
    /**
     * Sets the name of the rule.
     * @param name the name of the rule.
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Returns the resources of the rule.
     * @return the resources of the rule.
     */
    public List<Resource> getResources() {
        return resources;
    }

    public Map<String,Resource> getResourcesMap() {
    	Map <String, Resource> resourcesMap = new HashMap<String, Resource>();
    	for(Resource resource:getResources())
    		resourcesMap.put(resource.getKeyForMap(), resource);
    	return resourcesMap;
    }

    /**
     * Sets the resources of the rule.
     * @param resources the resources of the rule.
     */
    public void setResources(List<Resource> resources) {
        this.resources = resources;
    }

    /**
     * Returns the subjects of the rule.
     * @return the subjects of the rule.
     */
    public List<Subject> getSubjects() {
        return subjects;
    }

    public Map<String,Subject> getSubjectsMap() {
    	Map <String, Subject> subjectsMap = new HashMap<String, Subject>();
    	for(Subject subject:getSubjects())
    		subjectsMap.put(subject.getKeyForMap(), subject);
    	return subjectsMap;
    }

    /**
     * Sets the subjects of the rule.
     * @param subjects the subjects of the rule.
     */
    public void setSubjects(List<Subject> subjects) {
        this.subjects = subjects;
    }

    /**
     * Returns the policy to which this rule belongs.
     * @return the policy to which this rule belongs.
     */
    public String getPolicy() {
        return policy;
    }

    /**
     * Sets the policy to which the rule belongs.
     * @param policy the policy to which the rule belongs.
     */
    public void setPolicy(String policy) {
        this.policy = policy;
    }

    /**
     * Returns the actions of the rule.
     * @return the actions of the rule.
     */
    public List<Action> getActions() {
        return actions;
    }

    public Map<String,Action> getActionsMap() {
    	Map <String, Action> actionsMap = new HashMap<String, Action>();
    	for(Action action:getActions())
    		actionsMap.put(action.getKeyForMap(), action);
    	return actionsMap;
    }

    /**
     * Sets the actions of the rule.
     * @param actions the actions of the rule.
     */
    public void setActions(List<Action> actions) {
        this.actions = actions;
    }

    /**
     * Adds a subject to the rule.
     * @param subject the subject to be added.
     */
/*
    public void addSubject(XACMLAttributeElement subject) {
        subjects.add((Subject) subject);
    }
*/
    /**
     * Returns the utility object for this rule.
     * @return the utility object of the rule.
     */
    public Umu_xacml_util getUMU_XACML() {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();

        ElementoRule elementoRule = (ElementoRule) umu_xacml_util.createPrincipal(ElementoRule.TIPO_RULE);
        elementoRule.getAtributos().put("RuleId", name);
        elementoRule.getAtributos().put("Effect", policy);

        ElementoTarget elementoTarget = (ElementoTarget) umu_xacml_util.createChild(elementoRule, ElementoTarget.TIPO_TARGET);
        //Resources
        if (!resources.contains(Resource.ALLSELECTED) && !resources.isEmpty()) {
            ElementoResources elementoResources = (ElementoResources) umu_xacml_util.createChild(elementoTarget, ElementoResources.TIPO_RESOURCES);
            for (Resource resource : resources) {
                umu_xacml_util.insertChild(elementoResources, resource.getUMU_XACML());
            }
        }
        // Subjects
        if (!subjects.contains(Subject.ALLSELECTED) && !subjects.isEmpty()) {
            ElementoSubjects elementoSubjects = (ElementoSubjects) umu_xacml_util.createChild(elementoTarget, ElementoSubjects.TIPO_SUBJECTS);
            for (Subject subject : subjects) {
                umu_xacml_util.insertChild(elementoSubjects, subject.getUMU_XACML());
            }
        }
        // Actions
        if (!actions.contains(Action.ALLSELECTED) && !actions.isEmpty()) {
            ElementoActions elementoActions = (ElementoActions) umu_xacml_util.createChild(elementoTarget, ElementoActions.TIPO_ACTIONS);
            for (Action action : actions) {
                umu_xacml_util.insertChild(elementoActions, action.getUMU_XACML());
            }
        }
        return umu_xacml_util;
    }


    @Override
    public boolean equals(Object obj) {
    	if(obj == null) return false;
    	return 	 this.toString().equals(obj.toString());
    }

    
    @Override
    public String toString() {
        return this.getClass().getName() +": [ name: " + name + "  ]";
    }
    
}
