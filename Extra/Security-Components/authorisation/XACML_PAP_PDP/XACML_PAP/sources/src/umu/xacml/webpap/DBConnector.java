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
import umu.xacml.webpap.dbmanager.DBManager;
import umu.xacml.webpap.dbmanager.DiskDBManager;
import umu.xacml.webpap.dbmanager.ExistDBManager;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;


import org.xml.sax.SAXException;

import xacmleditor.*;

/**
 * This class represents a connector to a database to manage policies, resources and subjects.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class DBConnector {

    static private String connector;
    static private String diskConnectorConfigPath;
    static private String existConnectorConfigPath;
    static private Properties diskConnectorProperties;
    static private Properties existConnectorProperties;
    /**
     * Connector that reads and stores data in disk files.
     */
    static public final String DISK_CONNECTOR = "DISK_CONNECTOR";
    /**
     * Connector that makes use of an eXist XML database for data storage.
     */
    static public final String EXIST_CONNECTOR = "EXIST_CONNECTOR";

    /**
     * Initializes the connector with the specified configuration file.
     * @param configFilePath path to the configuration file.
     * @throws Exception if an error occurs.
     */
    static public void init(String configFilePath) throws Exception {
        loadConfigFile(configFilePath);
    }

    /**
     * Loads a given configuration file.
     * @param configFilePath path to the configuration file.
     * @throws Exception if an error occurs.
     */
    static protected void loadConfigFile(String configFilePath) throws Exception {
        Properties properties = new Properties();
        try {
            properties.loadFromXML(new FileInputStream(configFilePath));
            Enumeration<Object> keys = properties.keys();
            for (; keys.hasMoreElements();) {
                String actual = (String) keys.nextElement();
                setProperty(actual, properties.getProperty(actual));
            }
            diskConnectorProperties = new Properties();
            File file = new File(diskConnectorConfigPath.trim());
            if (!file.exists()) {
                Logger.getLogger(DBConnector.class.getName()).log(Level.WARNING, "disk connector config file does not exist: " + diskConnectorConfigPath);
            } else {
                diskConnectorProperties.loadFromXML(new FileInputStream(diskConnectorConfigPath.trim()));
            }
            existConnectorProperties = new Properties();
            file = new File(existConnectorConfigPath.trim());
            if (!file.exists()) {
                Logger.getLogger(DBConnector.class.getName()).log(Level.WARNING, "eXist connector config file does not exist: " + existConnectorConfigPath);
            } else {
                existConnectorProperties.loadFromXML(new FileInputStream(existConnectorConfigPath.trim()));
            }
        } catch (IOException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    static void saveConfig(String connector, Properties properties) {
        try {
            if (connector.equals(DBConnector.DISK_CONNECTOR)) {
                diskConnectorProperties = properties;
                FileOutputStream fileOutputStream = new FileOutputStream(diskConnectorConfigPath.trim());
                diskConnectorProperties.storeToXML(fileOutputStream, null);
            } else if (connector.equals(DBConnector.EXIST_CONNECTOR)) {
                existConnectorProperties = properties;
                FileOutputStream fileOutputStream = new FileOutputStream(existConnectorConfigPath.trim());
                existConnectorProperties.storeToXML(fileOutputStream, null);
            }
        } catch (IOException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        }
        DBConnector.connector = connector;
        dbConnector = new DBConnector(connector);
    }

    /**
     * Sets a property of the connector configuration. The following properties can be set:
     * 
     * CONNECTOR
     * DISK_CONNECTOR_CONFIG_PATH
     * EXIST_CONNECTOR_CONFIG_PATH
     * 
     * @param current the name of the property.
     * @param property the value of the property.
     * @throws Exception if an error occurs.
     */
    static protected void setProperty(String current, String property) throws Exception {
        if (current.equals("CONNECTOR")) {
            connector = property;
        }
        if (current.equals("DISK_CONNECTOR_CONFIG_PATH")) {
            diskConnectorConfigPath = property;
        }
        if (current.equals("EXIST_CONNECTOR_CONFIG_PATH")) {
            existConnectorConfigPath = property;
        }
    }

    static Properties getCurrentDiskParameter() {
        return diskConnectorProperties;
    }

    static Properties getCurrentExistParameter() {
        return existConnectorProperties;
    }

    static List<String> getDiskParameters() {
        return DiskDBManager.neededConfigParameters();
    }

    static List<String> getExistParameters() {
        return ExistDBManager.neededConfigParameters();
    }

    static String getCurrentDBConnectorName() {
        return connector;
    }
    /**
     * [ALL-SELECTED] constant.
     */
    public final String ALLSELECTED = "[ALL-SELECTED]";
    /**
     * Rule map.
     */
    public Map<String, Rule> ruleMap = new HashMap<String, Rule>();
    static private DBConnector dbConnector = null;

    /**
     * Returns the DB connector.
     * @return the DB connector.
     */
    static public DBConnector getDBConnector() {
        if (dbConnector == null) {
            dbConnector = new DBConnector(connector);
        }
        return dbConnector;
    }

    /**
     * Creates a new DB connector of a given type (DISK_CONNECTOR or EXIST_CONNECTOR).
     * @param connector the type of connector.
     */
    public DBConnector(String connector) {
        if (connector.equals(DISK_CONNECTOR)) {
            dbManager = new DiskDBManager(diskConnectorProperties);
        } else if (connector.equals(EXIST_CONNECTOR)) {
            dbManager = new ExistDBManager(existConnectorProperties);
        }
    }
    private DBManager dbManager;

    /**
     * Loads the policies.
     * @return the loaded policies.
     */
    public List<Policy> loadPolicies() {
        List<Policy> policies = new ArrayList<Policy>();

        String policySet = dbManager.retrievePolicySet();
        if(policySet.equals("") || policySet == null)
        	return policies;
        
        try {
            Umu_xacml_util umu_xacml_util = new Umu_xacml_util(policySet);
            ElementoXACML elementoPrincipal = umu_xacml_util.getPrincipal();
            if (elementoPrincipal instanceof ElementoPolicySet) {
                
            	ElementoPolicySet elementoPolicySet = (ElementoPolicySet) elementoPrincipal;
                
            	Iterator<ElementoXACML> it2 = umu_xacml_util.getChildren(
            								elementoPolicySet, 
            								ElementoPolicy.TIPO_POLICY).iterator();
                
            	while (it2.hasNext()) {
                    ElementoPolicy elementoPolicy = (ElementoPolicy) it2.next();
                    Policy policy = new Policy(umu_xacml_util, elementoPolicy);
                    policies.add(policy);
                }
            	
            } else if (elementoPrincipal instanceof ElementoPolicy) {
                ElementoPolicy elementoPolicy = (ElementoPolicy) elementoPrincipal;
                Policy policy = new Policy(umu_xacml_util, elementoPolicy);
                policies.add(policy);
            }
        } catch (IOException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        } catch (SAXException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        }
        return policies;
    }




    Policy importPolicy(String data) {
        try {
            Umu_xacml_util umu_xacml_util = new Umu_xacml_util(data);
            ElementoXACML elementoPrincipal = umu_xacml_util.getPrincipal();
            if (elementoPrincipal instanceof ElementoPolicy) {
                ElementoPolicy elementoPolicy = (ElementoPolicy) elementoPrincipal;
                Policy policy = new Policy(umu_xacml_util, elementoPolicy);
                return policy;
            }
        } catch (IOException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        } catch (SAXException ex) {
            Logger.getLogger(DBConnector.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }


    void storeXACMLAttributes(List<XACMLAttributeElement> attributes)throws IOException {
        dbManager.storeXACMLAttributes(attributes);
        
    }

    List<XACMLAttributeElement> getXACMLAttributes()  throws IOException {
    	return dbManager.getXACMLAttributes();
    }
    
    void storePolicies(List<Policy> policies) {
        Umu_xacml_util umu_xacml_util = new Umu_xacml_util();
        ElementoPolicySet elementoPolicySet = (ElementoPolicySet) umu_xacml_util.createPrincipal(ElementoPolicySet.TIPO_POLICYSET);
        elementoPolicySet.getAtributos().put("xmlns",
                "urn:oasis:names:tc:xacml:2.0:policy:schema:os");
        elementoPolicySet.getAtributos().put("PolicySetId", "POLICY_SET");
        elementoPolicySet.getAtributos().put("PolicyCombiningAlgId", "urn:oasis:names:tc:xacml:1.0:policy-combining-algorithm:first-applicable");
        umu_xacml_util.createChild(elementoPolicySet, ElementoTarget.TIPO_TARGET);

        for (Policy policy : policies) {
            umu_xacml_util.insertChild(elementoPolicySet, policy.getUMU_XACML());
        }

        dbManager.storePolicySet(umu_xacml_util.toString());
    }
}
