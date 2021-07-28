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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import org.zkoss.zk.ui.Executions;
import org.zkoss.zk.ui.util.GenericForwardComposer;
import org.zkoss.zul.Grid;
import org.zkoss.zul.Label;
import org.zkoss.zul.Radio;
import org.zkoss.zul.Radiogroup;
import org.zkoss.zul.Row;
import org.zkoss.zul.Textbox;

/**
 * This class contains handler methods for the configuration page (configuration.zul) events.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class EventControllerConfiguration extends GenericForwardComposer {

    private List<Row> diskParameters = new ArrayList<Row>();
    private List<Row> existParameters = new ArrayList<Row>();
    private Grid parameterGrid;
    private Radio rbDisk;
    private Radio rbExist;
    private Radiogroup rg1;

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
        // VerifySession();               
        loadConfiguration();
    }

    /**
     * Handler method for the rg1 radio group check.
     */
    public void onCheck$rg1() {
        parameterGrid.getRows().getChildren().clear();
        if (rbDisk.isChecked()) {
            for (Row row : diskParameters) {
                parameterGrid.getRows().appendChild(row);
            }
        } else if (rbExist.isChecked()) {
            for (Row row : existParameters) {
                parameterGrid.getRows().appendChild(row);
            }
        }
    }

    /**
     * Handler method for the save button click.
     */
    public void onClick$btSave() {
        saveConfig();
    }

    private void redirectBack() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    private void redirectBegin() {
        Executions.getCurrent().sendRedirect("index.zul");
    }

    private void loadConfiguration() {
        loadDiskParameters();
        loadExistParameters();
        String connectorName = DBConnector.getCurrentDBConnectorName();
        if (connectorName.equals(DBConnector.DISK_CONNECTOR)) {
            rbDisk.setChecked(true);
            for (Row row : diskParameters) {
                parameterGrid.getRows().appendChild(row);
            }
        } else if (connectorName.equals(DBConnector.EXIST_CONNECTOR)) {
            rbExist.setChecked(true);
            for (Row row : existParameters) {
                parameterGrid.getRows().appendChild(row);
            }
        }
    }

    private void loadDiskParameters() {
        Properties diskProperties = DBConnector.getCurrentDiskParameter();
        List<String> neededParameters = DBConnector.getDiskParameters();
        for (String parameter : neededParameters) {
            String value = diskProperties.getProperty(parameter, "");
            Row row = createRow(parameter, value);
            diskParameters.add(row);
        }
    }

    private void loadExistParameters() {
        Properties diskProperties = DBConnector.getCurrentExistParameter();
        List<String> neededParameters = DBConnector.getExistParameters();
        for (String parameter : neededParameters) {
            String value = diskProperties.getProperty(parameter, "");
            Row row = createRow(parameter, value);
            existParameters.add(row);
        }
    }

    private Row createRow(String key, String value) {
        Row row = new Row();
        Label label = new Label(key);
        Textbox textbox = new Textbox();
        textbox.setText(value);
        textbox.setWidth("100%");
        row.appendChild(label);
        row.appendChild(textbox);
        return row;
    }

    private void saveConfig() {
        String connector;
        if (rbExist.isChecked()) {
            connector = DBConnector.EXIST_CONNECTOR;
        } else {
            connector = DBConnector.DISK_CONNECTOR;
        }
        Properties properties = getProperties();
        DBConnector.saveConfig(connector, properties);
    }

    private Properties getProperties() {
        Properties properties = new Properties();
        List children = parameterGrid.getRows().getChildren();
        Iterator it = children.iterator();
        while (it.hasNext()) {
            Object object = it.next();
            if (object instanceof Row) {
                Row row = (Row) object;
                List rowChildren = row.getChildren();
                String key = "";
                String value = "";
                Iterator it2 = rowChildren.iterator();
                while (it2.hasNext()) {
                    Object object1 = it2.next();
                    if (object1 instanceof Label) {
                        Label label = (Label) object1;
                        key = label.getValue();
                    }
                    if (object1 instanceof Textbox) {
                        Textbox textbox = (Textbox) object1;
                        value = textbox.getText();
                    }
                }
                properties.setProperty(key, value);
            }
        }
        return properties;
    }
}
