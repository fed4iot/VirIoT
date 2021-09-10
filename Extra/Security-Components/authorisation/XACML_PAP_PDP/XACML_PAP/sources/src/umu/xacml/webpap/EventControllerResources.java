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
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.commons.lang.StringUtils;
import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.util.GenericForwardComposer;
import org.zkoss.zul.Listbox;
import org.zkoss.zul.Listitem;


// TODO: Los mapas pueden transformarse en Listas, simple y llanamente. No hay necesidad de usar Mapas. 

/**
 * This class contains handler methods for the manage resources page (manageResources.zul) events.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class EventControllerResources extends GenericForwardComposer {

    private List<Action> 		actionsList 	= new ArrayList<Action>();
    private List<Subject> 		subjectsList 	= new ArrayList<Subject>();
    private List< Resource> 	resourcesList 	= new ArrayList<Resource>();

    
    private Listitem selectedResource = null;
    private Listitem selectedAction	  = null;
    private Listitem selectedSubject  = null;
    
    Listbox resourceList_GUI;
    Listbox actionList_GUI;
    Listbox subjectList_GUI;
    
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

    /**
     * Handler method for the principal window creation.
     */
    public void onCreate$principal() {
        loadResources();
    }

    /**
     * Handler method for the new resource button click.
     */
    public void onClick$btNewResource() {
        newResource();
    }

    /**
     * Handler method for the delete resource button click.
     */
    public void onClick$btDeleteResource() {
        delResource();
    }

    /**
     * Handler method for the new action button click.
     */
    public void onClick$btNewAction() {
        newAction();
    }
    
    /**
     * Handler method for the delete action button click.
     */
    public void onClick$btDeleteAction() {
        delAction();
    }

    /**
     * Handler method for the new action button click.
     */
    public void onClick$btNewSubject() {
        newSubject();
    }
    
    /**
     * Handler method for the delete action button click.
     */
    public void onClick$btDeleteSubject() {
        delSubject();
    }
    
    /**
     * Handler method for the save button click.
     */
    
//TODO: Implementar la posibilidad de guardar
    public void onClick$btSave() {
        saveResource();
    }


    private void redirectBack() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    private void redirectBegin() {
        Executions.getCurrent().sendRedirect("index.zul");
    }


    /**
     * Handler method for the resource list selection.
     */
    public void onSelect$resourceList() {
        if (resourceList_GUI.getSelectedCount() == 1) {
            selectedResource = resourceList_GUI.getSelectedItem();
        }
    }

    public void onSelect$subjectList() {
        if (subjectList_GUI.getSelectedCount() == 1) {
            selectedSubject= subjectList_GUI.getSelectedItem();
        }
    }

    public void onSelect$actionList() {
        if (actionList_GUI.getSelectedCount() == 1) {
            selectedAction= actionList_GUI.getSelectedItem();
        }
    }

    
    void refreshDisplay(){
    	BasicWindowController.fillListWithListableArray(new ArrayList<XACMLAttributeElement>(subjectsList), subjectList_GUI);
    	BasicWindowController.fillListWithListableArray(new ArrayList<XACMLAttributeElement>(actionsList), actionList_GUI);
    	BasicWindowController.fillListWithListableArray(new ArrayList<XACMLAttributeElement>(resourcesList), resourceList_GUI);
    }
       
	///////////////////////////////////////////////////////////////////////////
	// ..\../..\../..\../..\../ Controller Behavior ..\../..\../..\../..\../ //
	///////////////////////////////////////////////////////////////////////////
    
    private void saveResource(){
    	List<XACMLAttributeElement> listOfAttributes = new ArrayList<XACMLAttributeElement>();
    	listOfAttributes.addAll(subjectsList);
    	listOfAttributes.addAll(actionsList);
    	listOfAttributes.addAll(resourcesList);
    	
    	try {
			DBConnector.getDBConnector().storeXACMLAttributes(listOfAttributes);
		} catch (IOException e) {
			BasicWindowController.showErrorMessageWindow("The Attributes could not be saved.");
			return;
		}
    	System.out.println("Resources Saved Correctly.");
    }

	////////////////////////////////
	// Resources Related Behavior //
	////////////////////////////////
    
    private void loadResources() {
    	
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
	            	resourcesList.add((Resource)r);
	            	break;
	            case Action.sortingParameter:
	            	actionsList.add((Action)r);
	            	break;
	            case Subject.sortingParameter:
	            	subjectsList.add((Subject)r);
	            	break;
	        	default:
	    			BasicWindowController.showErrorMessageWindow("The stored values where tampered with and are not consistent");
        	}
        }
		
		refreshDisplay();
    }

    private void deleteXACMLElementFromMapKey(String mapKey, List<?> list){
    	XACMLAttributeElement elementToRemove = null;
    	for(Object element: list)
    		
    		if(element instanceof XACMLAttributeElement &&  ((XACMLAttributeElement)element).getKeyForMap().equals(mapKey))
    		{
    			
    			System.out.println("Se va a eliminar: "+element);
    			elementToRemove = (XACMLAttributeElement)element;
    			break;
    		}
    	System.out.println("before: \n"+list);
    	list.remove(elementToRemove);
    	System.out.println("after: \n"+list);
    	
    }
    
    private void deleteXACMLElement(Listbox listbox,  List<?> list){
    	for (Object o :  listbox.getSelectedItems()) 
            //list.remove( ((Listitem) o).getLabel());
    		deleteXACMLElementFromMapKey(((Listitem) o).getLabel(),list);
    	System.out.println("after: \n"+list);

    }


	/////////////////////////////////
	// Validation Related Behavior //
	/////////////////////////////////
    
    private boolean isValidResourceName(Resource name) {
    	return !resourcesList.contains(name);
    }
    
    private boolean isValidActionName(Action name) {
    	return !actionsList.contains(name);
    }
    
    private boolean isValidSubjectName(Subject name) {
    	return !subjectsList.contains(name);
    }
    
    
	/////////////////////////////
	// Window Related Behavior //
	/////////////////////////////

    private boolean getResourceNameWindow(){
        BasicWindowController.showWindow("resourceName.zul");
        String resourceName = (String) sessionScope.get("resourcename");
        String resourceID = (String) sessionScope.get("resourceid");
        
        if (resourceName == null || resourceName.equals("") || StringUtils.countMatches(resourceName, " ") == resourceName.length() ||
        	resourceID == null || resourceID.equals("") || StringUtils.countMatches(resourceID, " ") == resourceID.length())
        { 	
        	BasicWindowController.showErrorMessageWindow("No resource name was entered");
            Logger.getLogger(EventControllerResources.class.getName()).log(Level.SEVERE, null, new InterruptedException("No resource name was entered"));
        	return false;
        }
        
    	if (!isValidResourceName(new Resource(resourceName,resourceID))) {
			BasicWindowController.showErrorMessageWindow("Resource already exist");
			return false;
		}

        return true;
    }
    
    
    public boolean getActionWindow(){
    	BasicWindowController.showWindow("actionName.zul");
        String actionName = (String) sessionScope.get("actionname");
        String actionID = (String) sessionScope.get("actionID");
        
        // TODO: Do de isValidActionName with the action Object and checking it agains the current list.  
        Action action = new Action(actionName,actionID);
        
        if (actionName == null || actionID == null
        	|| 	actionName.equals("") || actionID.equals("")|| StringUtils.countMatches(actionName, " ") == actionName.length()
        	|| 	actionID.equals("") || actionID.equals("")|| StringUtils.countMatches(actionID, " ") == actionID.length())
        {
        	BasicWindowController.showErrorMessageWindow("No action name or action id introduced");
            Logger.getLogger(EventControllerResources.class.getName()).log(Level.SEVERE, null, new InterruptedException("No action name or action id introduced"));

        	return false;
        }
        
		if (!isValidActionName(new Action(actionName,actionID))){
			BasicWindowController.showErrorMessageWindow("Subject Name already exist");
			return false;
		}
        
        return true;
    }
    
    public boolean getSubjectNameWindow() {

		BasicWindowController.showWindow("subjectName.zul");
		String subjectName = (String) sessionScope.get("subjectname");
		String subjectID = (String) sessionScope.get("subjectID");

		// Error checking
		if (subjectName == null || subjectName.equals("") ||  StringUtils.countMatches(subjectName, " ") == subjectName.length() ||
				subjectID == null || subjectID.equals("") ||  StringUtils.countMatches(subjectID, " ") == subjectID.length()) {
			BasicWindowController.showErrorMessageWindow("No Subject Name Entered");
			return false;
		}
		if (!isValidSubjectName(new Subject(subjectName,subjectID))) {
			BasicWindowController.showErrorMessageWindow("Subject Name already exist");
			return false;
		}
		return true;
	}

    
	//////////////////////////////
	// Subject Related Behavior //
	//////////////////////////////

    
    private void newResource() {

    	// Error Checking
    	if(!getResourceNameWindow())
    		return;

    	String resourceName = (String) sessionScope.get("resourcename");
    	String resourceID = (String) sessionScope.get("resourceid");

	    // Create the new Resource
	    Resource resource = new Resource(resourceName,resourceID);
        resourcesList.add(resource);
        refreshDisplay();
        System.out.println(resourcesList);
    }

    private void delResource() {
    	deleteXACMLElement(resourceList_GUI, resourcesList);
    	refreshDisplay();
    }
    
    
	//////////////////////////////
	//  Action Related Behavior //
	//////////////////////////////


    private void newAction() {
    	if(!getActionWindow())
    		return; 
    	
        Action action = new Action(	(String)sessionScope.get("actionname"),
        							(String)sessionScope.get("actionID"));
        
        actionsList.add(action);       	
    	refreshDisplay();
    	System.out.println(actionsList);
    }

    private void delAction() {
    	deleteXACMLElement(actionList_GUI, actionsList);
    	refreshDisplay();
    }

    
	/////////////////////////////////
	//  Subject Related Behavior //
	/////////////////////////////////

    private void newSubject() {
    	
    	if(!getSubjectNameWindow())
    		return;  
    	
    	 Subject subject= new Subject(	(String)sessionScope.get("subjectname"),
					(String)sessionScope.get("subjectID"));

    	 subjectsList.add(subject);        	
    	 refreshDisplay();
     	System.out.println(subjectsList);
    }
    
    private void delSubject() {
    	deleteXACMLElement(subjectList_GUI,subjectsList);
    	refreshDisplay();
    }

}
