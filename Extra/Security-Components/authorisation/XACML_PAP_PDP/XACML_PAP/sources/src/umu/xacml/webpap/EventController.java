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

import java.util.logging.Level;
import java.util.logging.Logger;
import org.zkoss.zhtml.Messagebox;
import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.util.GenericForwardComposer;

/**
 * This class contains handler methods for the main page (index.zul) events.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class EventController extends GenericForwardComposer {

    /**
     * Handler method for the manage policies button click.
     */
    public void onClick$managePolicies() {
        Executions.getCurrent().sendRedirect("managePolicies.zul");
    }

    /**
     * Handler method for the manage resources button click.
     */
    public void onClick$manageResources() {
        Executions.getCurrent().sendRedirect("manageResources.zul");
    }

    /**
     * Handler method for the manage subjects button click.
     */
    public void onClick$manageSubjects() {
        Executions.getCurrent().sendRedirect("manageSubjects.zul");
    }

    /**
     * Handler method for the index window creation.
     */
    public void onCreate$index() {
        initConnector();
    }

    /**
     * Handler method for the exit button click.
     */
    public void onClick$exit() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    /**
     * Handler method for the configuration button click.
     */
    public void onClick$configuration() {
        Executions.getCurrent().sendRedirect("configuration.zul");
    }

    private void initConnector() {
        try {
            DBConnector.init(this.application.getRealPath("/WEB-INF/config.xml"));
        	//DBConnector.init(this.application.getRealPath("/Users/dangarcia/Documents/EclilpseWorkspaces/XACML_PAP/XACML-WebPAP/WebContent/WEB-INF/config.xml"));
        } catch (Exception ex) {
            try {
				Messagebox.show("There was a problem reading configuration information, for further information see log files", "Error", Messagebox.OK, Messagebox.ERROR);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
            Logger.getLogger(EventController.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
