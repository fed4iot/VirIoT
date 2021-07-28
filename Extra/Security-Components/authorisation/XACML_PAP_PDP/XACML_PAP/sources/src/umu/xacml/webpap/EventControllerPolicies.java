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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.zkoss.util.media.Media;
import org.zkoss.zhtml.Messagebox;
import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.SuspendNotAllowedException;
import org.zkoss.zk.ui.event.DropEvent;
import org.zkoss.zk.ui.event.Event; //Added
import org.zkoss.zk.ui.event.EventListener; //Added
import org.zkoss.zk.ui.util.GenericForwardComposer;
import org.zkoss.zul.Button;
import org.zkoss.zul.Checkbox;
import org.zkoss.zul.Fileupload; //Added
import org.zkoss.zul.ListModel; //Added
import org.zkoss.zul.Listbox;
import org.zkoss.zul.Listcell; //Added
import org.zkoss.zul.Listitem;
import org.zkoss.zul.SimpleListModel; //Added
import org.zkoss.zul.Window; //Added

import blockchain.Blockchain; //Added
import umu.xacml.webpap.BasicWindowController;

/**
 * This class contains handler methods for the manage policies page (managePolicies.zul) events.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class EventControllerPolicies extends GenericForwardComposer {

	// Information to be shown in the GUI
    private Map<String, Policy> policyMap 	= new HashMap<String,Policy>();
    private List<Rule> 			ruleList	= new ArrayList<Rule>();
    
    private Map<String,Action> 	actionsMap 	= new HashMap<String,Action>();
    private Map<String,Subject> subjectsMap = new HashMap<String,Subject>();
    private Map<String,Resource>resourcesMap= new HashMap<String,Resource>();
    
    private Listitem selectedRule = null;
    private Listitem selectedPolicy = null;

    // GUI Attributes
    
    Button btNewPolicy;
    Button btApply;
    Button btNewRule;
    Button btDelRule;
    Button btSave;
    Button btRuleUP;
    Button btRuleDOWN;

    Listbox policyList_GUI;
    Listbox ruleList_GUI;

    Listbox cbRuleCA;
    Listbox cbRule;

    Listbox resourceList_GUI;
    Listbox actionList_GUI;
    Listbox subjectList_GUI;
    
    
    Checkbox chBAllActions;
    Checkbox chBAllResources;
    Checkbox chBAllSubjects;

	////////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../ General Aux Functions..\../..\../..\../..\../ //
	////////////////////////////////////////////////////////////////////////////

    /**
     * Preconditions: 
     * 	- The key oldkey exists in the map
     *  - The key newkey does not exists in the map 
     */
    private boolean rekeyPolicyMapElement(Map<String,Policy> map, String oldkey, String newkey){
    	if(map.containsKey(newkey) || !map.containsKey(oldkey))
    		return false;
    	Policy renamingElement = map.remove(oldkey);
    	map.put(newkey, renamingElement);
    	return true;
    }    
    
    
	//////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../ General Controller ..\../..\../..\../..\../ //
	//////////////////////////////////////////////////////////////////////////

    
   
    void refreshDisplay()
    {
    	BasicWindowController.fillListWithMapKey(policyMap, policyList_GUI);
    	BasicWindowController.fillListWithMap(new HashMap<String,XACMLAttributeElement>(subjectsMap), subjectList_GUI);
    	BasicWindowController.fillListWithMap(new HashMap<String,XACMLAttributeElement>(actionsMap), actionList_GUI);
    	BasicWindowController.fillListWithMap(new HashMap<String,XACMLAttributeElement>(resourcesMap), resourceList_GUI);
    	cbRule.setDisabled(true);
    	selectedPolicy();
    }
       
    /////////////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../Controller Policies & Rules..\../..\../..\../..\../ //
	/////////////////////////////////////////////////////////////////////////////////
    
    
  private void loadXACMLAttributes() {
    	
        List<XACMLAttributeElement> xacmlAttsList = null;
		try {
			xacmlAttsList = DBConnector.getDBConnector().getXACMLAttributes();
		} catch (IOException e) {
			BasicWindowController.showErrorMessageWindow("There was an error loading the information");
		}
		
		System.out.println("There are "+ xacmlAttsList.size() + " attributes loaded");        
		for (XACMLAttributeElement r : xacmlAttsList) {
        	
        	System.out.println(r.toString());
        	
        	switch(r.getSortedValue()){
	            case Resource.sortingParameter:
	            	resourcesMap.put(r.getKeyForMap(),(Resource)r);
	            	break;
	            case Action.sortingParameter:
	            	actionsMap.put(r.getKeyForMap(),(Action)r);
	            	break;
	            case Subject.sortingParameter:
	            	subjectsMap.put(r.getKeyForMap(),(Subject)r);
	            	break;
	        	default:
	    			BasicWindowController.showErrorMessageWindow("The stored values where tampered with and are not consistent");
        	}
        }
		
		refreshDisplay();
    }

  //
  //	Helpers
  //

  boolean isValidPolicyName(String name) {
  	return !BasicWindowController.isStringInListBox(name, policyList_GUI);
  }

  //
  // Load Functions
  //
	private void loadPolicies() {
	    List<Policy> policiesList = DBConnector.getDBConnector().loadPolicies();
	
	    for (Policy policy: policiesList)
	    	policyMap.put(policy.getName(), policy);
	
	    refreshDisplay();
	}
    
	void emptyAndDeactivateAll(){
     	BasicWindowController.deativateAllItemsInList(actionList_GUI);
     	BasicWindowController.deativateAllItemsInList(subjectList_GUI);
     	BasicWindowController.deativateAllItemsInList(resourceList_GUI);
        chBAllActions.setChecked(false);
        chBAllSubjects.setChecked(false);
        chBAllResources.setChecked(false);

	}
	
    void selectedPolicy() {
     	
     	selectedPolicy = policyList_GUI.getSelectedItem();
     	if (selectedPolicy == null) 
    		return; 

     	// Empty Everything
     	emptyAndDeactivateAll();
     	
     	// Fill the rules of the policy
        Policy policy = policyMap.get(selectedPolicy.getLabel());
        BasicWindowController.fillListWithNamedObject(new ArrayList<NamedObject>(policy.getRules()), ruleList_GUI);
        BasicWindowController.setSelectOption(policy.getCombiningAlg(), cbRuleCA);
        
        
        
        // Debug information
     	System.out.println("Function selectedPolicy()");
        System.out.println("Filling all the rules. "+policy.getRules().size() + " rules in this policy");
        
    }

    //
    // 	Window Funcions
    //
    public boolean showPolicyNameWindow(){
      	
    	ruleList_GUI.getChildren().clear();
        if(!BasicWindowController.showWindow("policyName.zul"))
        	return false;

        String policyName = (String) sessionScope.get("policyname");

        if(policyName == null || policyName == "")
        	return false;

        if (!isValidPolicyName(policyName)) 
        {
        	BasicWindowController.showErrorMessageWindow("Policy Name already exist");
        	return false;
        }
        
        return true;
    }
    
    
    void newPolicy() {
     
        if(!showPolicyNameWindow())
        	return; 
        
        String policyName = (String) sessionScope.get("policyname");
        Policy policy = new Policy(policyName);

        policyMap.put(policy.getName(), policy);

        refreshDisplay();
        selectedPolicy = BasicWindowController.setSelectedInList(policyName,policyList_GUI);
        emptyAndDeactivateAll();
        
        return;
    }

    
    void renamePolicy() {
    	
      	if(selectedPolicy == null){
    		BasicWindowController.showErrorMessageWindow("No Policy Selected to be renamed");
    		return;
    	}

        if(!showPolicyNameWindow())
        	return; 

        String newPolicyName = (String) sessionScope.get("policyname");
        String oldPolicyName = selectedPolicy.getLabel();
        rekeyPolicyMapElement(policyMap,oldPolicyName,newPolicyName);

        refreshDisplay();
    }

   
    void deletePolicies() {
    	
    	boolean result = BasicWindowController.showQuestionMessageWindow("Selected policies will be deleted, do you wish to continue? \n Warning, it could not be undone", "Delete rules");
    	if(!result) return;
   		
		for (Listitem li: (Set<Listitem>) policyList_GUI.getSelectedItems())
			policyMap.remove(li.getLabel());
	
		ruleList.clear();
		ruleList_GUI.getChildren().clear();
		refreshDisplay();
    }
    

    /**
     * Applies the selected policy.
     */
    public void applyPolicy(){
        DBConnector.getDBConnector().storePolicies(getPolicies());

        String currrentHash="";

        String BC_Int = (System.getenv("BlockChain_integration") != null) ? System.getenv("BlockChain_integration") : "0";

		if(BC_Int.equals("1")) {

            try {
                currrentHash = Blockchain.getCurrentHash();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            BasicWindowController.showQuestionMessageWindow("New Hash: " + currrentHash, "OK!");

        }
 		       
    }
    
    private List<Policy> getPolicies() {
        ArrayList<Policy> policies = new ArrayList<Policy>();
        for(Entry<String, Policy>policy: policyMap.entrySet())
        	policies.add(policy.getValue());
        return policies;
    }


//////////////////////////////////////////////////////////////////////
//..\../..\../..\../..\../Controller Rules ..\../..\../..\../..\../ //
//////////////////////////////////////////////////////////////////////

    private boolean getNewRuleWindow()
    {
    	
      	if(selectedPolicy == null){
    		BasicWindowController.showErrorMessageWindow("No Policy Selected associate a Rule");
    		return false;
    	}
      	
    	if(!BasicWindowController.showWindow("ruleName.zul"))
    		return false;
    	
        String ruleName = (String) sessionScope.get("rulename");
        if(ruleName == null || ruleName == "")
        	return false;
        
        if (!isValidRuleName(ruleName))
        {
        	BasicWindowController.showErrorMessageWindow("Rule name already exist");
        	return false; 
        }

        return true;        
    }
    
    void newRule() {
    
    	if(!getNewRuleWindow())
    		return;

    	String ruleName = (String) sessionScope.get("rulename");
    	
    	Rule rule = new Rule(ruleName);
    	// TODO: delete comment
    	//  Esto se puede hacer añadiendo a una lista en vez de a un mapa
    	policyMap.get(selectedPolicy.getLabel())
        		 .getRules()
        		 .add(rule);
    	
    	selectedPolicy();
        selectedRule = BasicWindowController.setSelectedInList(ruleName,ruleList_GUI);
        selectedRule();
    }
    
    boolean isValidRuleName(String name) {
    	return !BasicWindowController.isStringInListBox(name, ruleList_GUI);
    }

	void deleteRules() {
    	
    	boolean result  = BasicWindowController.showQuestionMessageWindow("Selected rules wil be deleted, Do you wish to continue?", "Delete Rules");
    	if(!result)
    		return;
    	
		for (Listitem li: (Set<Listitem>) ruleList_GUI.getSelectedItems())
		// Se puede eliminar elemento por nombre en la lista, no hace falta mapa
		{
			//ruleMap.remove(li.getLabel());
			policyMap.get(selectedPolicy.getLabel()).deleteRuleByName(li.getLabel());
		}

		// Update policyMap and Refresh GUI
		// Se puede cambiar por una lista en vez de un mapa
		//policyMap.get(selectedPolicy.getLabel()).setRules(ruleMap);
		selectedPolicy();
		
    }

    void selectedRule() {

    	System.out.println("selectedRule()");
    	if(ruleList_GUI.getSelectedCount() != 1)
    		return;
    	
    	// Clear all the Related Attributes to fill the new ones
        resourceList_GUI.	clearSelection();
        subjectList_GUI.	clearSelection();
        actionList_GUI.		clearSelection();
        chBAllResources.	setChecked(false);
        chBAllSubjects.		setChecked(false);
        chBAllActions.		setChecked(false);

        selectedRule 		= ruleList_GUI.getSelectedItem();
        //Rule rule = ruleMap.get(selectedRule.getLabel());
        Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());
    	cbRule.setDisabled(false);
        BasicWindowController.setSelectOption(rule.getPolicy(), cbRule);
        
        // Cheching Resources
        if(rule.getResources().contains(Resource.ALLSELECTED)){
        	changeChAll(resourceList_GUI,true);
        	chBAllResources.setChecked(true);
        }else{
        	changeChAll(resourceList_GUI,false);

        	// Se puede usar una lista en lugar de un mapa para las relgas
        	Map<String,NamedObject> resourcesToCheckMap 
        	= new HashMap<String,NamedObject>(policyMap	.get(selectedPolicy.getLabel())
        												.getRuleByName(selectedRule.getLabel())
        												.getResourcesMap());
        	
        	BasicWindowController
        	.checkItemsFromMap(resourcesToCheckMap, new HashMap<String,NamedObject>(resourcesMap), resourceList_GUI);
       }
        

        // Cheching Subjects
        if(rule.getSubjects().contains(Subject.ALLSELECTED)){
        	changeChAll(subjectList_GUI,true);
        	chBAllSubjects.setChecked(true);
        }else{
        	changeChAll(subjectList_GUI,false);
        	Map<String,NamedObject> subjectsToCheckMap 
        	= new HashMap<String,NamedObject>(policyMap	.get(selectedPolicy.getLabel())
														.getRuleByName(selectedRule.getLabel())
														.getSubjectsMap());
        	
        	BasicWindowController
        	.checkItemsFromMap(subjectsToCheckMap, new HashMap<String,NamedObject>(subjectsMap), subjectList_GUI);
       }

        if(rule.getActions().contains(Action.ALLSELECTED)){
        	changeChAll(actionList_GUI,true);
            chBAllActions.setChecked(true);
        }else{
        	changeChAll(actionList_GUI,false);
        	Map<String,NamedObject> actionsToCheckMap 
        	= new HashMap<String,NamedObject>(policyMap	.get(selectedPolicy.getLabel())
        												.getRuleByName(selectedRule.getLabel())
														.getActionsMap());
        	
        	BasicWindowController
        	.checkItemsFromMap(actionsToCheckMap, new HashMap<String,NamedObject>(actionsMap), actionList_GUI);
       }

    
    
    }
    

	//////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../Controller Resources..\../..\../..\../..\../ //
	//////////////////////////////////////////////////////////////////////////
    
    
    void changeChAll(Listbox list, boolean disabled){
    	for (Object object : list.getItems()) 
            ((Listitem) object).setDisabled(disabled);
    }
    
    void changeChBAllResources() {
        for (Object object : resourceList_GUI.getItems()) 
            ((Listitem) object).setDisabled(chBAllResources.isChecked());
    }
    
    void changeChBAllActions() {
        for (Object object : actionList_GUI.getItems()) 
            ((Listitem) object).setDisabled(chBAllActions.isChecked());
    }

  
    void changeChBAllSubjects() {
        for (Object object : subjectList_GUI.getItems()) 
        	((Listitem) object).setDisabled(chBAllSubjects.isChecked());
    }



    private void subjectSelected() {
    	System.out.println("calling subjectSelected() ");

    	if(selectedRule == null)
    	{
    		System.out.println("selectedRule is NULL");
    		return; 
    	}

    	Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());

    	 // IF THE CHECKALL BUTTON HAS BEEN CHECKED
    	 if(chBAllSubjects.isChecked()){
    		   rule.getSubjects().add(Subject.ALLSELECTED);
    	 }
    	 else
    	 {

	    	rule.getSubjects().remove(Subject.ALLSELECTED);
	
	    	List<Subject> subjects = new ArrayList<Subject>();
	
	    	System.out.println("Subjects in the rule before adding the changes");
	    	for (Subject subject: rule.getSubjects())
	    		System.out.println(subject);
	    	
	    	for(Object li: subjectList_GUI.getChildren()){
	    		if( ((Listitem)li).isSelected())
	    		{
	    			System.out.println("SELECTED "+ ((Listitem)li).getLabel());
	    			subjects.add(subjectsMap.get( ((Listitem)li).getLabel() ) );
	    		}
	    		else
	    			System.out.println("UNSELECTED "+ ((Listitem)li).getLabel());
	    	}
	    	
	    	// Now we save the rule in the Policy
			rule.setSubjects(subjects);
    	 }
    }

    void resourceSelected() {


    	System.out.println("calling resourceSelected() ");

    	if(selectedRule == null)
    	{
    		System.out.println("selectedRule is NULL");
    		return; 
    	}

    	Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());

    	 // IF THE CHECKALL BUTTON HAS BEEN CHECKED
    	 if(chBAllResources.isChecked()){
	 		rule.getResources().add(Resource.ALLSELECTED);
    	 }
    	 else
    	 {

    		rule.getResources().remove(Resource.ALLSELECTED);
	    	List<Resource> resources = new ArrayList<Resource>();
	
	    	System.out.println("Resources in the rule before adding the changes");
	    	for (Resource resource: rule.getResources())
	    		System.out.println(resource);
	    	
	    	for(Object li: resourceList_GUI.getChildren()){
	    		if( ((Listitem)li).isSelected())
	    		{
	    			System.out.println("SELECTED "+ ((Listitem)li).getLabel());
	    			resources.add(resourcesMap.get( ((Listitem)li).getLabel() ) );
	    		}
	    		else
	    			System.out.println("UNSELECTED "+ ((Listitem)li).getLabel());
    	}
    	
    	// Now we save the rule in the Policy
 		rule.setResources(resources); 	
    	 }
    	
    }
    
    
    void actionSelected() {

    	System.out.println("calling actionSelected() ");

    	if(selectedRule == null)
    	{
    		System.out.println("selectedRule is NULL");
    		return; 
    	}
    	Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());

    	 // IF THE CHECKALL BUTTON HAS BEEN CHECKED
    	 if(chBAllActions.isChecked()){
	 		rule.getActions().add(Action.ALLSELECTED);
    	 }
    	 else
    	 {
	 		rule.getActions().remove(Action.ALLSELECTED);

	    	List<Action> actions = new ArrayList<Action>();
	
	    	System.out.println("Actions in the rule before adding the changes");
	    	for (Action action: rule.getActions())
	    		System.out.println(action);
	    	
	    	for(Object li: actionList_GUI.getChildren()){
	    		if( ((Listitem)li).isSelected())
	    		{
	    			System.out.println("SELECTED "+ ((Listitem)li).getLabel());
	    			actions.add(actionsMap.get( ((Listitem)li).getLabel() ) );
	    		}
	    		else
	    			System.out.println("UNSELECTED "+ ((Listitem)li).getLabel());
	    	}
    	
    		rule.setActions(actions);
    	 }
   	
    }

    
    void ruleUp() {
		System.out.println("RuleUP");

		List <Rule> ruleList = policyMap.get(selectedPolicy.getLabel()).getRules(); 
		Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());
   		int index = ruleList.indexOf(rule);

   		System.out.println("The intended index to remove is "+index);
   		System.out.println("The size of the Rule list is "+ruleList.size());
   		if(index <= 0)
   			return;

   		
   		ruleList.add(index-1, ruleList.remove(index));
        
   		selectedPolicy();
   		selectedRule = BasicWindowController.setSelectedInList(rule.getName(),ruleList_GUI);
        selectedRule();
    }


    void ruleDown() {
   		System.out.println("RuleDown");
   		
		List <Rule> ruleList = policyMap.get(selectedPolicy.getLabel()).getRules(); 
		Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());
   		int index = ruleList.indexOf(rule);

   		System.out.println("The intended index to remove is "+index);
   		System.out.println("The size of the Rule list is "+ruleList.size());

   		if(index == ruleList.size()-1 || index < 0)
   				return;
   		
   		ruleList.add(index+1, ruleList.remove(index));

   		selectedPolicy();
        selectedRule = BasicWindowController.setSelectedInList(rule.getName(),ruleList_GUI);
        selectedRule();
    }

   
    void importPolicy() {
    	// TODO: ESTO NO FUNCIONABA, LO HE QUITADO.
    }


    private void defineObligations() {
    // TODO: FALTA POR AÑADIR

    }    

    private void modifiedPolicy(){

    	System.out.println("modifiedPolicy");
    	if(selectedPolicy == null)
    		return;


    	Policy policy = policyMap.get(selectedPolicy.getLabel());
        policy.setCombiningAlg(cbRuleCA.getSelectedItem().getLabel());
    	
    }

    private void modifiedRule(){
    	System.out.println("modifiedRule");

    	if(selectedRule == null)
    		return;
    	
    	Rule rule = policyMap.get(selectedPolicy.getLabel()).getRuleByName(selectedRule.getLabel());
        rule.setPolicy(cbRule.getSelectedItem().getLabel());
   	
    }
    

	///////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../GUI Handling Behavior..\../..\../..\../..\../ //
	///////////////////////////////////////////////////////////////////////////

    /**
     * Handler method for the back button click.
     */
    public void onClick$back() {
        redirectBack();
    }

    /**
     * Handler method for the begin button click.
     */
    public void onClick$begin() {
        redirectBegin();
    }

    private void redirectBack() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    private void redirectBegin() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    /**
     * Handler method for the principal window creation.
     */
    public void onCreate$principal() {
        loadPolicies();
        loadXACMLAttributes();
    }

    /**
     * Handler method for the new policy button click.
     */
    public void onClick$btNewPolicy() {
        newPolicy();
    }

    public void onSelect$cbRuleCA() {
    	modifiedPolicy();
    }

    public void onSelect$cbRule() {
    	modifiedRule();
    }
    
    /**
     * Handler method for the delete policy button click.
     */
    public void onClick$btDeletePolicy() {
        deletePolicies();
    }

    /**
     * Handler method for the import policy button click.
     */
    public void onClick$btImportPolicy() {
        importPolicy();
    }

    /**
     * Handler method for the resource list selection.
     */
    public void onSelect$resourceList_GUI() {
        resourceSelected();
    }
    
    /**
     * Handler method for the all resources check box check.
     */
    public void onCheck$chBAllResources() {
        changeChBAllResources();
        resourceSelected();
    }

    /**
     * Handler method for the subject list selection.
     */
    public void onSelect$subjectList_GUI() {
        subjectSelected();
    }

    /**
     * Handler method for the all subjects check box check.
     */
    public void onCheck$chBAllSubjects() {
        changeChBAllSubjects();
        subjectSelected();
    }

    /**
     * Handler method for the action list selection.
     */
    public void onSelect$actionList_GUI() {
        actionSelected();
    }

    /**
     * Handler method for the all actions check box check.
     */
    public void onCheck$chBAllActions() {
        changeChBAllActions();
        actionSelected();
    }

    /**
     * Handler method for the rule list selection.
     */
    public void onSelect$ruleList_GUI() {
        selectedRule();
    }

    /**
     * Handler method for the new rule button click.
     */
    public void onClick$btNewRule() {
        newRule();
    }

    /**
     * Handler method for the delete rule button click.
     */
    public void onClick$btDelRule() {
        deleteRules();
    }

    /**
     * Handler method for the rule up button click.
     */
    public void onClick$btRuleUP() {
        ruleUp();
    }

    /**
     * Handler method for the rule down button click.
     */
    public void onClick$btRuleDOWN() {
        ruleDown();
    }

    /**
     * Handler method for the apply button click.
     */
    public void onClick$btApply() {
     
    	
    	applyPolicy();
    }

    /**
     * Handler method for the obligations popup click.
     */
    public void onClick$popupObligations() {
        defineObligations();
    }

    /**
     * Handler method for the rename popup click.
     */
    public void onClick$btRenamePolicy() {
        renamePolicy();
    }

    /**
     * Handler method for the policy list selection.
     */
    public void onSelect$policyList_GUI() {
    	cbRule.setDisabled(true);
    	selectedPolicy();
    }




}
