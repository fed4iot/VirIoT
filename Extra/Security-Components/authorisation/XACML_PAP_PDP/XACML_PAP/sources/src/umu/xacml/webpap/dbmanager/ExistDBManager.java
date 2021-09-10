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
package umu.xacml.webpap.dbmanager;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import java.util.ArrayList;
import java.util.List;
import java.util.Properties;


import org.xmldb.api.DatabaseManager;
import org.xmldb.api.base.Collection;
import org.xmldb.api.base.Database;
import org.xmldb.api.base.XMLDBException;
import org.xmldb.api.modules.CollectionManagementService;

import umu.xacml.webpap.XACMLAttributeElement;

/**
 * This class represents a database manager that makes use of an eXist XML database.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 * @author Dan García Carrillo
 */
public class ExistDBManager implements DBManager {

    private String existDBURL = null;
    private String existDBUser = null;
    private String existDBPassword = null;
    private String policiesURI = null;
    private String xacmlAttsURI = null;
    
    private final String driver = "org.exist.xmldb.DatabaseImpl";
    /**
     * ALL-ROLES constant.
     */
    static public final String ALL_ROLE_NAME = "ALL-ROLES";
    /**
     * ALL-PERMIT-ATTRIBUTES constant.
     */
    static public final String ALL_PERMIT_ATTRIBUTES = "ALL-PERMIT-ATTRIBUTES";
    static private final String NULL_ATTRIBUTE = "NULL_ATTRIBUTE";
    private String baseURI = null;

    /**
     * Returns the list of needed configuration parameters for this DB manager.
     * @return the list of needed configuration parameters.
     */
    public static List<String> neededConfigParameters() {
        List<String> configParameters = new ArrayList<String>();
        configParameters.add("EXIST_DB_URL");
        configParameters.add("EXIST_DB_USER");
        configParameters.add("EXIST_DB_PASSWORD");
        configParameters.add("POLICIES_URI");
        return configParameters;
    }

    /**
     * Constructor to create the database manager. Unknown parameters should be set as null.
     * @param properties the configuration parameters.
     */
    public ExistDBManager(Properties properties) {
    }

    /**
     * Constructor to create the database manager. Unknown parameters should be set as null.
     * @param existDBURL URL of eXist database listening XMLDB protocol, e.g. xmldb:exist://localhost:8080/exist/xmlrpc/db/
     * @param existDBUser eXist user with read or write permission.
     * @param existDBPassword eXist password of the user.
     */
    public ExistDBManager(String existDBURL, String existDBUser, String existDBPassword) {
        this.existDBURL = existDBURL;
        this.existDBUser = existDBUser;
        this.existDBPassword = existDBPassword;
        this.baseURI = existDBURL + "pap/";
        this.policiesURI = baseURI + "policies/";
        this.xacmlAttsURI = baseURI + "xacmlAtt/";
    }

    private boolean createExistCollection(String URI, String collection) {
        try {
            Class cl = Class.forName(driver);
            Database database = (Database) cl.newInstance();
            DatabaseManager.registerDatabase(database);

            // Get the collection
            Collection col = DatabaseManager.getCollection(URI + collection, existDBUser, existDBPassword);
            if (col == null) {
                Collection root = DatabaseManager.getCollection(URI, existDBUser, existDBPassword);
                CollectionManagementService mgtService = (CollectionManagementService) root.getService("CollectionManagementService", "1.0");
                col = mgtService.createCollection(collection);
            }
            return true;
        } catch (XMLDBException ex) {
            Logger.getLogger(ExistDBManager.class.getName()).log(Level.SEVERE, null, ex);
        } catch (InstantiationException ex) {
            Logger.getLogger(ExistDBManager.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IllegalAccessException ex) {
            Logger.getLogger(ExistDBManager.class.getName()).log(Level.SEVERE, null, ex);
        } catch (ClassNotFoundException ex) {
            Logger.getLogger(ExistDBManager.class.getName()).log(Level.SEVERE, null, ex);
        }
        return false;
    }

    /**
     * Prepare exist databases to work                 
     * @return true if succeeded to prepare the database. false otherwise.
     */
    public boolean createBBDD() {
        if (createExistCollection(existDBURL, "pap")
                && createExistCollection(baseURI, "policies")
                && createExistCollection(baseURI, "xacmlAtts")) {
            return true;
        } else {
            return false;
        }

    }

    /**
     * Check if is established an eXist-DB connection
     * @return true if an eXist-DB connection is established. false otherwise.
     */
    public boolean checkExist() {
        try {
            Class cl = Class.forName(driver);
            Database database = (Database) cl.newInstance();
            DatabaseManager.registerDatabase(database);

            // get the collection
            if (DatabaseManager.getCollection(policiesURI, existDBUser, existDBPassword) == null) {
                return false;
            }
            return true;
        } catch (Exception ex) {
            return false;
        }
    }


    @Override
    public String retrievePolicySet() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public void storePolicySet(String policySet) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

	@Override
	public List<XACMLAttributeElement> getXACMLAttributes() throws IOException {
        throw new UnsupportedOperationException("Not supported yet.");
	}

	@Override
	public void storeXACMLAttributes(List<XACMLAttributeElement> attributes) throws IOException {
        throw new UnsupportedOperationException("Not supported yet.");		
	}
}
