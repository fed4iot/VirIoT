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

import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.SuspendNotAllowedException;
import org.zkoss.zk.ui.util.GenericForwardComposer;
import org.zkoss.zul.Listbox;
import org.zkoss.zul.Listitem;
import org.zkoss.zul.Messagebox;
import org.zkoss.zul.Window;


public final class BasicWindowController extends GenericForwardComposer{

	private static final long serialVersionUID = 1L;
	
////////////////////////////////////////////////////////////////////////////////////////////
//										GUI BEHAVIOR									  //
////////////////////////////////////////////////////////////////////////////////////////////

	// FILLING THE LIST
	
	public static void fillListWithMapKey(Map<?,?> data, Listbox list){		
		list.getChildren().clear();
		for (Entry<?,?> entry: data.entrySet()){
			 list.appendItem(entry.getKey().toString(),"");			
		}
	}

	public static void fillListWithMapValue(Map<?,?> data, Listbox list){		
		list.getChildren().clear();
		for (Entry<?,?> entry: data.entrySet()){
			 list.appendItem(entry.getValue().toString(),"");			
		}
	}

	public static void fillListWithMap(Map<?,XACMLAttributeElement> data, Listbox list){		
		list.getChildren().clear();
		for (Entry<?,?> entry: data.entrySet()){
			 Listitem listitem = list.appendItem(((XACMLAttributeElement)entry.getValue()).getKeyForMap(),null);

 /*
			THIS CODE IS TO SEPARATE IN TWO ROWS THE INFORMATION
			 Listcell listcell = new Listcell();
			 listcell.setLabel( ((XACMLAttributeElement)entry.getValue()).getXACMLID());
             listitem.appendChild(listcell);
*/
		}
	}

	public static void setSelectOption(String value, Listbox list){

		System.out.println("setSelectOption");

		int numberOfItems = list.getItemCount();
		for(int i=0; i< numberOfItems; i++)
		{
			System.out.println(list.getItemAtIndex(i).getLabel());
			if(list.getItemAtIndex(i).getLabel().equals(value))
			{
				list.setSelectedIndex(i);
				return;
			}
		}
		System.out.println("Not found!");
	}
	
	public static void fillListWithListableArray(List<XACMLAttributeElement> data, Listbox list){		
		
		list.getChildren().clear();
		
		for(XACMLAttributeElement item: data){
			if(item instanceof Listable){
//			 Entry<String,String> entry = (Entry<String, String>) ((Listable) item).getListableMessage();
			 Listitem listitem = list.appendItem(item.getKeyForMap(),null);

/*
  	THIS CODE IS TO SEPARATE IN TWO ROWS THE INFORMATION
			 Listcell listcell = new Listcell();
             listcell.setLabel(entry.getValue());
             listitem.appendChild(listcell);
*/
			}
		}
	}
	
	public static void fillListWithNamedObject(List<NamedObject> data, Listbox list){
		list.getChildren().clear();
		for(Object item: data){
			 Listitem listitem = list.appendItem(((NamedObject)item).getName(),null);
		}
	}
	
	
	
	public static boolean isStringInListBox(String element, Listbox list){
		// TODO: CHECK WHERE THIS FUNCTION IS USED TO CHECK THE WORK IS CORRECT
		Iterator it = list.getChildren().iterator();
	        while (it.hasNext()) {
	            Listitem listitem = (Listitem) it.next();
	            String elemName = listitem.getLabel();
	            if (elemName.equals(element)) {
	                return true;
	            }
	        }
	        return false;
	}

	public static Listitem setSelectedInList(String name, Listbox list){
		for(Object li: list.getItems())
			if(  ((Listitem)li).getLabel().equals(name))
			{
				((Listitem)li).setSelected(true);
				return ((Listitem)li);
			}
		return null;
	}
	
	public static void checkItemsFromMap(Map<String, NamedObject> attributesToSelect, Map<String, NamedObject> allAttributes, Listbox list){

		System.out.println("checkItemsFromMap()");
		list.getChildren().clear();

		for(Entry<String,NamedObject> allAttributesEntry: allAttributes.entrySet()){
			System.out.print("allAttributesEntry: "+allAttributesEntry.getKey());
			Listitem appendedItem = list.appendItem(allAttributesEntry.getKey().toString(),allAttributesEntry.getValue().toString());			
			if( attributesToSelect.containsKey(allAttributesEntry.getKey())){
				appendedItem.setSelected(true);
				System.out.print(" - CHECKED ");
			}else{
				System.out.print(" - UNCHECKED ");
			}
			
			System.out.println();

		}
		
		
	}
	
	// Modifying THE LIST
	public static void deativateAllItemsInList(Listbox list){
		if(list != null && list.getItemCount() > 0)
        for (Object object : list.getItems()) {
            Listitem listItem = (Listitem) object;
            listItem.setDisabled(true);
        }
	}
	
	
	////////////////////////////////////////////////////////////////////////////////////////////
	//										WINDOW BEHAVIOR									  //
	////////////////////////////////////////////////////////////////////////////////////////////
	
	public static boolean showQuestionMessageWindow(String question, String statement){

		int response = 0;
		try {
			response = Messagebox.show(
					question,
					statement, Messagebox.OK | Messagebox.CANCEL, Messagebox.QUESTION);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		if (response == Messagebox.CANCEL) {
			return false;
		}
		return true;
	}
	
	public static void showErrorMessageWindow(String information){
			try {
				Messagebox.show(information, "Error", Messagebox.OK, Messagebox.ERROR);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
	}
	

	
	public static boolean showWindow(String filename){
		final Window win = (Window) Executions.createComponents(filename, null, null);
		try {
			win.doModal();
		} catch (SuspendNotAllowedException | InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return true;
	}
	
}
