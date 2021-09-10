
/*
 * @(#)FilePolicyModule.java
 *
 * Copyright 2003-2004 Sun Microsystems, Inc. All Rights Reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *   1. Redistribution of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 * 
 *   2. Redistribution in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *
 * Neither the name of Sun Microsystems, Inc. or the names of contributors may
 * be used to endorse or promote products derived from this software without
 * specific prior written permission.
 * 
 * This software is provided "AS IS," without a warranty of any kind. ALL
 * EXPRESS OR IMPLIED CONDITIONS, REPRESENTATIONS AND WARRANTIES, INCLUDING
 * ANY IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 * OR NON-INFRINGEMENT, ARE HEREBY EXCLUDED. SUN MICROSYSTEMS, INC. ("SUN")
 * AND ITS LICENSORS SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY LICENSEE
 * AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
 * DERIVATIVES. IN NO EVENT WILL SUN OR ITS LICENSORS BE LIABLE FOR ANY LOST
 * REVENUE, PROFIT OR DATA, OR FOR DIRECT, INDIRECT, SPECIAL, CONSEQUENTIAL,
 * INCIDENTAL OR PUNITIVE DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY
 * OF LIABILITY, ARISING OUT OF THE USE OF OR INABILITY TO USE THIS SOFTWARE,
 * EVEN IF SUN HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
 *
 * You acknowledge that this software is not designed or intended for use in
 * the design, construction, operation or maintenance of any nuclear facility.
 */

package com.sun.xacml.finder.impl;

import com.sun.xacml.AbstractPolicy;
import com.sun.xacml.EvaluationCtx;
import com.sun.xacml.MatchResult;
import com.sun.xacml.Policy;
import com.sun.xacml.PolicySet;

import com.sun.xacml.ctx.Status;

import com.sun.xacml.finder.PolicyFinder;
import com.sun.xacml.finder.PolicyFinderModule;
import com.sun.xacml.finder.PolicyFinderResult;

import java.io.File;
import java.io.FileInputStream;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import java.util.logging.Level;
import java.util.logging.Logger;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;


/**
 * This module represents a collection of files containing polices,
 * each of which will be searched through when trying to find a
 * policy that is applicable to a specific request.
 * <p>
 * Note: this module is provided only as an example and for testing
 * purposes. It is not part of the standard, and it should not be
 * relied upon for production systems. In the future, this will likely
 * be moved into a package with other similar example and testing
 * code.
 *
 * @since 1.0
 * @author Seth Proctor
 */
public class FilePolicyModule extends PolicyFinderModule
    implements ErrorHandler
{

    /**
     * The property which is used to specify the schema
     * file to validate against (if any)
     */
    public static final String POLICY_SCHEMA_PROPERTY =
        "com.sun.xacml.PolicySchema";


    public static final String JAXP_SCHEMA_LANGUAGE =
        "http://java.sun.com/xml/jaxp/properties/schemaLanguage";
    
    public static final String W3C_XML_SCHEMA =
        "http://www.w3.org/2001/XMLSchema";

    public static final String JAXP_SCHEMA_SOURCE =
        "http://java.sun.com/xml/jaxp/properties/schemaSource";
    

    // the finder that is using this module
    private PolicyFinder finder;

    //
    private File schemaFile;

    //
    private Set fileNames;

    //
    private Set policies;

    // the logger we'll use for all messages
    private static final Logger logger =
        Logger.getLogger(FilePolicyModule.class.getName());

    /**
     * Constructor which retrieves the schema file to validate policies against
     * from the POLICY_SCHEMA_PROPERTY. If the retrieved property
     * is null, then no schema validation will occur.
     */
    public FilePolicyModule() {
        fileNames = new HashSet();
        policies = new HashSet();

        String schemaName = System.getProperty(POLICY_SCHEMA_PROPERTY);

        if (schemaName == null)
            schemaFile = null;
        else
            schemaFile = new File(schemaName);
    }

    /**
     * Constructor that uses the specified input as the schema file to
     * validate policies against. If schema validation is not desired,
     * a null value should be used.
     *
     * @param schemaFile the schema file to validate policies against,
     *                   or null if schema validation is not desired.
     */
    public FilePolicyModule(File schemaFile) {
        fileNames = new HashSet();
        policies = new HashSet();

        this.schemaFile = schemaFile;
    }

    /**
     * Constructor that specifies a set of initial policy files to use.
     * No schema validation is performed.
     *
     * @param fileNames a <code>List</code> of <code>String</code>s that
     *                  identify policy files
     */
    public FilePolicyModule(List fileNames) {
        this();

        if (fileNames != null)
            this.fileNames.addAll(fileNames);
    }

    /**
     * Indicates whether this module supports finding policies based on
     * a request (target matching). Since this module does support
     * finding policies based on requests, it returns true.
     *
     * @return true, since finding policies based on requests is supported
     */
    public boolean isRequestSupported() {
        return true;
    }

    /**
     * Initializes the <code>FilePolicyModule</code> by loading
     * the policies contained in the collection of files associated
     * with this module. This method also uses the specified 
     * <code>PolicyFinder</code> to help in instantiating PolicySets.
     *
     * @param finder a PolicyFinder used to help in instantiating PolicySets
     */
    public void init(PolicyFinder finder) {
        this.finder = finder;

        Iterator it = fileNames.iterator();
        while (it.hasNext()) {
            String fname = (String)(it.next());
            AbstractPolicy policy = loadPolicy(fname, finder,
                                               schemaFile, this);
            if (policy != null)
                policies.add(policy);
        }
    }

    /**
     * Adds a file (containing a policy) to the collection of filenames
     * associated with this module. 
     *
     * @param filename the file to add to this module's collection of files
     */
    public boolean addPolicy(String filename) {
        return fileNames.add(filename);
    }

    /**
     * Loads a policy from the specified filename and uses the specified
     * <code>PolicyFinder</code> to help with instantiating PolicySets.
     *
     * @param filename the file to load the policy from
     * @param finder a PolicyFinder used to help in instantiating PolicySets
     *
     * @return a (potentially schema-validated) policy associated with the 
     *         specified filename, or null if there was an error
     */
    public static AbstractPolicy loadPolicy(String filename,
                                            PolicyFinder finder) {
        return loadPolicy(filename, finder, null, null);
    }

    /**
     * Loads a policy from the specified filename, using the specified
     * <code>PolicyFinder</code> to help with instantiating PolicySets,
     * and using the specified input as the schema file to validate
     * policies against. If schema validation is not desired, a null
     * value should be used for schemaFile
     * 
     * @param filename the file to load the policy from
     * @param finder a PolicyFinder used to help in instantiating PolicySets
     * @param schemaFile the schema file to validate policies against, or
     *                   null if schema validation is not desired
     * @param handler an error handler used to print warnings and errors
     *                during parsing
     *
     * @return a (potentially schema-validated) policy associated with the 
     *         specified filename, or null if there was an error
     */
    public static AbstractPolicy loadPolicy(String filename,
                                            PolicyFinder finder,
                                            File schemaFile,
                                            ErrorHandler handler) {
        try {
            // create the factory
            DocumentBuilderFactory factory =
                DocumentBuilderFactory.newInstance();
            factory.setIgnoringComments(true);

            DocumentBuilder db = null;

            // as of 1.2, we always are namespace aware
            factory.setNamespaceAware(true);

            // set the factory to work the way the system requires
            if (schemaFile == null) {
                // we're not doing any validation
                factory.setValidating(false);

                db = factory.newDocumentBuilder();
            } else {
                // we're using a validating parser
                factory.setValidating(true);

                factory.setAttribute(JAXP_SCHEMA_LANGUAGE, W3C_XML_SCHEMA);
                factory.setAttribute(JAXP_SCHEMA_SOURCE, schemaFile);
                
                db = factory.newDocumentBuilder();
                db.setErrorHandler(handler);
            }

            // try to load the policy file
            Document doc = db.parse(new FileInputStream(filename));
            
            // handle the policy, if it's a known type
            Element root = doc.getDocumentElement();
            String name = root.getTagName();

            if (name.equals("Policy")) {
                return Policy.getInstance(root);
            } else if (name.equals("PolicySet")) {
                return PolicySet.getInstance(root, finder);
            } else {
                // this isn't a root type that we know how to handle
                throw new Exception("Unknown root document type: " + name);
            }

        } catch (Exception e) {
            if (logger.isLoggable(Level.WARNING))
                logger.log(Level.WARNING, "Error reading policy from file " +
                           filename, e);
        }

        // a default fall-through in the case of an error
        return null;
    }

    /**
     * Finds a policy based on a request's context. This may involve using
     * the request data as indexing data to lookup a policy. This will always
     * do a Target match to make sure that the given policy applies. If more
     * than one applicable policy is found, this will return an error.
     * NOTE: this is basically just a subset of the OnlyOneApplicable Policy
     * Combining Alg that skips the evaluation step. See comments in there
     * for details on this algorithm.
     *
     * @param context the representation of the request data
     *
     * @return the result of trying to find an applicable policy
     */
    public PolicyFinderResult findPolicy(EvaluationCtx context) {
        AbstractPolicy selectedPolicy = null;
        Iterator it = policies.iterator();

        while (it.hasNext()) {
            AbstractPolicy policy = (AbstractPolicy)(it.next());

            // see if we match
            MatchResult match = policy.match(context);
            int result = match.getResult();
            
            // if there was an error, we stop right away
            if (result == MatchResult.INDETERMINATE)
                return new PolicyFinderResult(match.getStatus());

            if (result == MatchResult.MATCH) {
                // if we matched before, this is an error...
                if (selectedPolicy != null) {
                    ArrayList code = new ArrayList();
                    code.add(Status.STATUS_PROCESSING_ERROR);
                    Status status = new Status(code, "too many applicable top-"
                                               + "level policies");
                    return new PolicyFinderResult(status);
                }

                // ...otherwise remember this policy
                selectedPolicy = policy;
            }
        }

        // if we found a policy, return it, otherwise we're N/A
        if (selectedPolicy != null)
            return new PolicyFinderResult(selectedPolicy);
        else
            return new PolicyFinderResult();
    }

    /**
     * Standard handler routine for the XML parsing.
     *
     * @param exception information on what caused the problem
     */
    public void warning(SAXParseException exception) throws SAXException {
        if (logger.isLoggable(Level.WARNING))
            logger.warning("Warning on line " + exception.getLineNumber() +
                           ": " + exception.getMessage());
    }

    /**
     * Standard handler routine for the XML parsing.
     *
     * @param exception information on what caused the problem
     *
     * @throws SAXException always to halt parsing on errors
     */
    public void error(SAXParseException exception) throws SAXException {
        if (logger.isLoggable(Level.WARNING))
            logger.warning("Error on line " + exception.getLineNumber() +
                           ": " + exception.getMessage() + " ... " +
                           "Policy will not be available");

        throw new SAXException("error parsing policy");
    }

    /**
     * Standard handler routine for the XML parsing.
     *
     * @param exception information on what caused the problem
     *
     * @throws SAXException always to halt parsing on errors
     */
    public void fatalError(SAXParseException exception) throws SAXException {
        if (logger.isLoggable(Level.WARNING))
            logger.warning("Fatal error on line " + exception.getLineNumber() +
                           ": " + exception.getMessage() + " ... " +
                           "Policy will not be available");

        throw new SAXException("fatal error parsing policy");
    }

}
