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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.util.logging.Level;
import java.util.logging.Logger;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map; //Added
import java.util.Properties;


import org.jdom.Document;
import org.jdom.Element;
import org.jdom.JDOMException;
import org.jdom.input.SAXBuilder;

import org.jdom.output.Format;
import org.jdom.output.XMLOutputter;

import blockchain.Blockchain;
import umu.xacml.webpap.Action;
import umu.xacml.webpap.Resource;
import umu.xacml.webpap.Subject;
import umu.xacml.webpap.XACMLAttributeElement;

/**
 * This class represents a database manager that reads and writes data to disk files.
 * 
 * @author Ginés Dólera Tormo
 * @author Juan M. Marín Pérez
 * @author Jorge Bernal Bernabé
 * @author Gregorio Martínez Pérez
 * @author Antonio F. Skarmeta Gómez
 */
public class DiskDBManager implements DBManager {

    /**
     * Returns the list of needed configuration parameters for this DB manager.
     * @return the list of needed configuration parameters.
     */
    public static List<String> neededConfigParameters() {
        List<String> configParameters = new ArrayList<String>();
        configParameters.add("POLICY_SET_PATH");
        configParameters.add("XACMLATTS_PATH");
        return configParameters;
    }

    private String policySetPath;
    private String xacmlAttributesPath;

	List<XACMLAttributeElement> xacmlAttributes = null;

    
    /**
     * Constructor to create the database manager. Unknown parameters should be set as null.
     * @param properties the configuration parameters.
     */
    public DiskDBManager(Properties properties) {
        policySetPath = properties.getProperty("POLICY_SET_PATH");
        xacmlAttributesPath = properties.getProperty("XACMLATTS_PATH");
    }

    @Override
    public String retrievePolicySet() {
        try {
            System.out.println("Retrieving the PolicySet from " + policySetPath);
        	StringBuilder fileData = new StringBuilder(1000);
            BufferedReader reader = new BufferedReader(
                    new FileReader(policySetPath));
            
            
            char[] buf = new char[1024];
            int numRead = 0;
            while ((numRead = reader.read(buf)) != -1) {
                String readData = String.valueOf(buf, 0, numRead);
                fileData.append(readData);
                buf = new char[1024];
            }
            reader.close();
            String policySet = fileData.toString();
            return policySet;
        } catch (IOException ex) {
            Logger.getLogger(DiskDBManager.class.getName()).log(Level.SEVERE, null, ex);
        }
        return "";
    }

    

    
    @Override
    public void storePolicySet(String policySet) {

    	FileWriter fw = null;
        try {
            File f = new File(policySetPath);
            fw = new FileWriter(f);
            fw.write(policySet);
        } catch (IOException ex) {
            Logger.getLogger(DiskDBManager.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                fw.close();
            } catch (IOException ex) {
                Logger.getLogger(DiskDBManager.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        String BC_Int = (System.getenv("BlockChain_integration") != null) ? System.getenv("BlockChain_integration") : "0";

		if(BC_Int.equals("1")) {

            try {
                Blockchain.registerOrUpdate(policySetPath);
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
        
    }

    public List<XACMLAttributeElement> getXACMLAttributes() {
  
// 	Load Always from file.     	
//        if (xacmlAttributes != null)
//        	return xacmlAttributes;

    	xacmlAttributes = new ArrayList<XACMLAttributeElement>();
    	File dir = new File(xacmlAttributesPath);
        FilenameFilter filter = new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                return name.endsWith(".xml");
            }
        };
        String[] children = dir.list(filter);
        if (children == null) {
        } else {
        	for (int i = 0; i < children.length; i++) {
                try {
                    String filename = children[i];
                    System.out.println("Searching for Attributes in the file: " + xacmlAttributesPath+ filename);
                    List<XACMLAttributeElement> parsedXACMLAttribute = parseXACMLAttributes(xacmlAttributesPath + filename);
                    xacmlAttributes.addAll(parsedXACMLAttribute);
                } catch (JDOMException ex) {
                    Logger.getLogger(DiskDBManager.class.getName()).log(Level.SEVERE, null, ex);
                } catch (IOException ex) {
                    Logger.getLogger(DiskDBManager.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        }
        return xacmlAttributes;

    }
    

    private List<XACMLAttributeElement> parseXACMLAttributes(String resourceFile) throws JDOMException, IOException {
    	List<XACMLAttributeElement> attributeList = new ArrayList<XACMLAttributeElement>();
    	
    	
        SAXBuilder builder = new SAXBuilder(false);
        File file = new File(resourceFile);
        Document doc = builder.build(file);
        Element root = doc.getRootElement();
        
        Element actionsElement = root.getChild("attributes");
        Iterator it = actionsElement.getChildren("attribute").iterator();
       
        while (it.hasNext()) {
            Element actionElement = (Element) it.next();
            String name = actionElement.getAttributeValue("name");
            String xacml_id = actionElement.getAttributeValue("xacml_id");
            String sortedValue = actionElement.getAttributeValue("sortedValue");
            // TODO: Esto aún está por incluir en el XACMLAttributeElement
            String xacml_DataType = actionElement.getAttributeValue("xacml_DataType");
            
            if(name != null && xacml_id != null && sortedValue != null)
            {
            	switch(sortedValue){
	            case Resource.sortingParameter:
	            	attributeList.add(new Resource(name,xacml_id));break;
	            case Action.sortingParameter:
	            	attributeList.add(new Action(name,xacml_id));break;
	            case Subject.sortingParameter:
	            	attributeList.add(new Subject(name,xacml_id));break;
	        	default:
	        		break;
            	}
            }
       }
        return attributeList;
    }

    

    @Override
    public void storeXACMLAttributes(List<XACMLAttributeElement> attributes) throws IOException {

    	
    	Element root = new Element("attributes");
        root.setAttribute("storingDate", LocalDateTime.now().toString());

        Document doc = new Document(root);
        Element attributesElm = new Element("attributes");
        root.getChildren().add(attributesElm);

        for (XACMLAttributeElement attribute : attributes) {
            Element attributeElm = new Element("attribute");
            attributeElm.setAttribute("name", attribute.getName());
            attributeElm.setAttribute("xacml_id", attribute.getXACMLID());
            attributeElm.setAttribute("sortedValue", attribute.getSortedValue());
            attributeElm.setAttribute("xacml_DataType", "#string");
            attributesElm.getChildren().add(attributeElm);
        }

        XMLOutputter outputter = new XMLOutputter(Format.getPrettyFormat());
        String content = outputter.outputString(doc);
        
        File inputFile = new File(xacmlAttributesPath + "XACML_Attributes.xml");
        FileWriter fw = new FileWriter(inputFile);
        BufferedWriter bw = new BufferedWriter(fw);
        bw.write(content);
        bw.close();
        fw.close();
    }


}
