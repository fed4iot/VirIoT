/*
 *    Copyright (C) 2012, 2013 Universidad de Murcia
 *
 *    Authors:
 *        Ginés Dólera Tormo <ginesdt@um.es>
 *        Juan M. Marín Pérez <juanmanuel@um.es>
 *        Jorge Bernal Bernabé <jorgebernal@um.es>
 *        Gregorio Martínez Pérez <gregorio@um.es>
 *        Antonio F. Skarmeta Gómez <skarmeta@um.es>
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

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.SuspendNotAllowedException;
import org.zkoss.zk.ui.util.GenericForwardComposer;
import org.zkoss.zul.Listbox;
import org.zkoss.zul.Listitem;
import org.zkoss.zul.Messagebox;
import org.zkoss.zul.Radio;
import org.zkoss.zul.Radiogroup;
import org.zkoss.zul.Window;

/**
 * This class contains handler methods for the policy obligations page (policyObligations.zul) events.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class EventControllerObligations extends GenericForwardComposer {

    private Map<String, Obligation> obligationMap = new HashMap<String, Obligation>();
    Window defineObligations;
    Listbox obligationList;
    Radiogroup rg1;
    Radio rbPermit;
    Radio rbDeny;

    /**
     * Handler method for the define obligations window creation.
     */
    public void onCreate$defineObligations() {
        loadObligations();
        rbPermit.setDisabled(true);
        rbDeny.setDisabled(true);
    }

    /**
     * Handler method for the new obligation button click.
     */
    public void onClick$btNewObligation() {
        newObligation();
    }

    /**
     * Handler method for the delete obligation button click.
     */
    public void onClick$btDeleteObligation() {
        delObligation();
    }

    /**
     * Handler method for the cancel button click.
     */
    public void onClick$btCancel() {
        cancel();
    }

    /**
     * Handler method for the ok button click.
     */
    public void onClick$btOk() {
        returnObligation();
    }

    /**
     * Handler method for the obligation list selection.
     */
    public void onSelect$obligationList() {
        obligationSelected();
    }

    /**
     * Handler method for the rg1 radio group check.
     */
    public void onCheck$rg1() {
        Obligation obligation = obligationMap.get(obligationList.getSelectedItem().getLabel());
        if (rbPermit.isChecked()) {
            obligation.setFulFillOn(Obligation.Fulfill.Permit);
        } else {
            obligation.setFulFillOn(Obligation.Fulfill.Deny);
        }
    }

    private void loadObligations() {
        List<Obligation> obligations = (List<Obligation>) sessionScope.get("policyobligations");
        if (obligations != null) {
            for (Obligation o : obligations) {
                obligationMap.put(o.getId(), o);
                Listitem listitem = obligationList.appendItem(o.getId(), null);
            }
        }
    }

    private void newObligation() {
        while (true) {
            final Window win = (Window) Executions.createComponents(
			        "obligationName.zul", null, null);
			try {
				win.doModal();
			} catch (SuspendNotAllowedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			} catch (InterruptedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}

			String obligationName = (String) sessionScope.get("obligationname");
			if (obligationName == null) {
			    return;
			} else {
			    if (isValidObligationName(obligationName)) {
			        Listitem listitem = obligationList.appendItem(obligationName, null);
			        Obligation obligation = new Obligation(obligationName);
			        obligationMap.put(obligationName, obligation);
			        rbPermit.setChecked(true);
			        rbPermit.setDisabled(false);
			        rbDeny.setDisabled(false);
			        obligationList.setSelectedItem(listitem);
			        return;
			    } else {
			        try {
						Messagebox.show("Obligation Name already exist", "Error", Messagebox.OK, Messagebox.ERROR);
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
			    }
			}
        }
    }

    private boolean isValidObligationName(String name) {
        Iterator it = obligationList.getChildren().iterator();
        while (it.hasNext()) {
            Listitem listitem = (Listitem) it.next();
            String obligationName = listitem.getLabel();
            if (obligationName.equals(name)) {
                return false;
            }
        }
        return true;
    }

    private void delObligation() {
        TreeSet<Integer> indexes = new TreeSet<Integer>(Collections.reverseOrder()) {
        };
        for (Object o : obligationList.getSelectedItems()) {
            Listitem item = (Listitem) o;
            indexes.add(item.getIndex());
        }

        for (Integer i : indexes) {
            Listitem listitem = obligationList.removeItemAt(i);
            // TODO: FIX needs to be congruent with the changes in Resource and Subject (views, Class and DBManagement) 
            //Resource toremove = obligationMap.remove(listitem.getLabel());
            //DBConnector.getDBConnector().deleteResource(toremove);
        }
        rbPermit.setDisabled(true);
        rbDeny.setDisabled(true);
    }

    private void obligationSelected() {
        if (obligationList.getSelectedCount() != 1) {
            rbPermit.setDisabled(true);
            rbDeny.setDisabled(true);
        } else {
            rbPermit.setDisabled(false);
            rbDeny.setDisabled(false);
            Obligation obligation = obligationMap.get(obligationList.getSelectedItem().getLabel());
            if (obligation.getFulFillOn().equals(Obligation.Fulfill.Permit)) {
                rbPermit.setChecked(true);
            } else {
                rbDeny.setChecked(true);
            }
        }
    }

    private void cancel() {
        sessionScope.put("policyobligations", null);
        defineObligations.detach();
    }

    private void returnObligation() {
        List<Obligation> obligations = new ArrayList<Obligation>(obligationMap.values());
        sessionScope.put("policyobligations", obligations);
        defineObligations.detach();
    }
}
