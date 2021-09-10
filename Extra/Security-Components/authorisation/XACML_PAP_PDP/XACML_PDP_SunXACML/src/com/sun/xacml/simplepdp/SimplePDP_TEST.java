package com.sun.xacml.simplepdp;
/*
 * @(#)SimplePDP.java
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


import com.sun.xacml.ConfigurationStore;
import com.sun.xacml.Indenter;
import com.sun.xacml.ParsingException;
import com.sun.xacml.PDP;
import com.sun.xacml.PDPConfig;

import com.sun.xacml.cond.FunctionFactory;
import com.sun.xacml.cond.FunctionFactoryProxy;
import com.sun.xacml.cond.StandardFunctionFactory;

import com.sun.xacml.ctx.RequestCtx;
import com.sun.xacml.ctx.ResponseCtx;

import com.sun.xacml.finder.AttributeFinder;
import com.sun.xacml.finder.PolicyFinder;

import com.sun.xacml.finder.impl.CurrentEnvModule;
import com.sun.xacml.finder.impl.FilePolicyModule;
import com.sun.xacml.finder.impl.SelectorModule;

import java.io.InputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileInputStream;
import java.io.IOException;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;


/**
 * This is a simple, command-line driven XACML PDP. It acts both as an example
 * of how to write a full-featured PDP and as a sample program that lets you
 * evaluate requests against policies. See the comments for the main() method
 * for correct usage.
 *
 * @since 1.1
 * @author seth proctor
 */
public class SimplePDP_TEST
{

    // this is the actual PDP object we'll use for evaluation
    private PDP pdp = null;

    /**
     * Default constructor. This creates a <code>SimplePDP</code> with a
     * <code>PDP</code> based on the configuration defined by the runtime
     * property com.sun.xcaml.PDPConfigFile.
     */
    public SimplePDP_TEST() throws Exception {
        // load the configuration
        ConfigurationStore store = new ConfigurationStore();

        // use the default factories from the configuration
        store.useDefaultFactories();

        // get the PDP configuration's and setup the PDP
        pdp = new PDP(store.getDefaultPDPConfig());
    }

    /**
     * Constructor that takes an array of filenames, each of which
     * contains an XACML policy, and sets up a <code>PDP</code> with access
     * to these policies only. The <code>PDP</code> is configured
     * programatically to have only a few specific modules.
     *
     * @param policyFiles an arry of filenames that specify policies
     */
    public SimplePDP_TEST(String [] policyFiles) throws Exception {
        // Create a PolicyFinderModule and initialize it...in this case,
        // we're using the sample FilePolicyModule that is pre-configured
        // with a set of policies from the filesystem
        FilePolicyModule filePolicyModule = new FilePolicyModule();
        for (int i = 0; i < policyFiles.length; i++)
            filePolicyModule.addPolicy(policyFiles[i]);

        // next, setup the PolicyFinder that this PDP will use
        PolicyFinder policyFinder = new PolicyFinder();
        Set policyModules = new HashSet();
        policyModules.add(filePolicyModule);
        policyFinder.setModules(policyModules);

        // now setup attribute finder modules for the current date/time and
        // AttributeSelectors (selectors are optional, but this project does
        // support a basic implementation)
        CurrentEnvModule envAttributeModule = new CurrentEnvModule();
        SelectorModule selectorAttributeModule = new SelectorModule();

        // Setup the AttributeFinder just like we setup the PolicyFinder. Note
        // that unlike with the policy finder, the order matters here. See the
        // the javadocs for more details.
        AttributeFinder attributeFinder = new AttributeFinder();
        List attributeModules = new ArrayList();
        attributeModules.add(envAttributeModule);
        attributeModules.add(selectorAttributeModule);
        attributeFinder.setModules(attributeModules);

        // Try to load the time-in-range function, which is used by several
        // of the examples...see the documentation for this function to
        // understand why it's provided here instead of in the standard
        // code base.
        FunctionFactoryProxy proxy =
            StandardFunctionFactory.getNewFactoryProxy();
        FunctionFactory factory = proxy.getConditionFactory();
        factory.addFunction(new TimeInRangeFunction());
        FunctionFactory.setDefaultFactory(proxy);

        // finally, initialize our pdp
        pdp = new PDP(new PDPConfig(attributeFinder, policyFinder, null));
    }

    /**
     * Evaluates the given request and returns the Response that the PDP
     * will hand back to the PEP.
     *
     * @param requestFile the name of a file that contains a Request
     *
     * @return the result of the evaluation
     *
     * @throws IOException if there is a problem accessing the file
     * @throws ParsingException if the Request is invalid
     */
    public ResponseCtx evaluate(String requestFile)
        throws IOException, ParsingException
    {
        // setup the request based on the file
        RequestCtx request =
            RequestCtx.getInstance(new FileInputStream(requestFile));

        // evaluate the request
        return pdp.evaluate(request);
    }


    /**
     * Evaluates the given request and returns the Response that the PDP
     * will hand back to the PEP.
     *
     * @param requestFile the name of a file that contains a Request
     *
     * @return the result of the evaluation
     *
     * @throws IOException if there is a problem accessing the file
     * @throws ParsingException if the Request is invalid
     */
    public ResponseCtx evaluateInputStream(InputStream requestStream)
        throws IOException, ParsingException
    {
        // setup the request based on the file
        RequestCtx request =
            RequestCtx.getInstance(requestStream);

        // evaluate the request
        return pdp.evaluate(request);
    }

    

    
    /**
     * Main-line driver for this sample code. This method lets you invoke
     * the PDP directly from the command-line.
     *
     * @param args the input arguments to the class. They are either the
     *             flag "-config" followed by a request file, or a request
     *             file followed by one or more policy files. In the case
     *             that the configuration flag is used, the configuration
     *             file must be specified in the standard java property,
     *             com.sun.xacml.PDPConfigFile.
     */
    public static void main(String [] args) throws Exception {
/*
        SimplePDP_TEST simplePDP = null;
        String [] policyFiles = new String[1];
        policyFiles[0] = "/Users/dangarcia/Desktop/PROYECTOS_DE_PROGRAMACION/[Project]PAP_PDP/DIFFERENT_PROJECTS/battery_of_tests/policies/policy_test2.xml";
        
        simplePDP = new SimplePDP_TEST(policyFiles);
                
        String req = "<Request xmlns=\"urn:oasis:names:tc:xacml:2.0:context:schema:os\">  <Subject SubjectCategory=\"urn:oasis:names:tc:xacml:1.0:subject-category:access-subject\">    <Attribute AttributeId=\"urn:oasis:names:tc:xacml:1.0:subject:subject-id\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>UMU</AttributeValue></Attribute>  </Subject>  <Resource>     <Attribute AttributeId=\"urn:oasis:names:tc:xacml:1.0:resource:resource-id\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>dev/digout/01/status</AttributeValue></Attribute>  </Resource>  <Action>    <Attribute AttributeId=\"urn:oasis:names:tc:xacml:1.0:action:action-id\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>POST</AttributeValue></Attribute>  </Action><Environment/></Request>";
        ResponseCtx response = simplePDP.evaluateInputStream(new ByteArrayInputStream(req.getBytes()));

        // for this sample program, we'll just print out the response
        response.encode(System.out, new Indenter());    
*/
    		
    	//Absolute path of XACML Policies (continue-a.xml)
    	String policyFile = "/Users/dangarcia/Desktop/PROYECTOS_DE_PROGRAMACION/[Project]PAP_PDP/DIFFERENT_PROJECTS/battery_of_tests/policies/policy_test2.xml";
    	
    	//String body of the PDP request
    	String XACMLRequest = "<Request xmlns=\"urn:oasis:names:tc:xacml:2.0:context:schema:os\">  <Subject SubjectCategory=\"urn:oasis:names:tc:xacml:1.0:subject-category:access-subject\">    <Attribute AttributeId=\"urn:ietf:params:scim:schemas:core:2.0:username\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>Pedro</AttributeValue></Attribute>  </Subject>  <Resource>     <Attribute AttributeId=\"urn:oasis:names:tc:xacml:1.0:resource:resource-id\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>https://123.123.123.123:1027/api/v1/resources</AttributeValue></Attribute>  </Resource>  <Action>    <Attribute AttributeId=\"urn:oasis:names:tc:xacml:1.0:action:action-id\" DataType=\"http://www.w3.org/2001/XMLSchema#string\"><AttributeValue>GET</AttributeValue></Attribute>  </Action><Environment/></Request>";
    	SimplePDP_TEST.test(policyFile, XACMLRequest);
    }

    
    public static String test(String policyFile, String XACMLRequest) throws Exception{
        SimplePDP_TEST simplePDP = null;
        //System.out.println(XACMLRequest);
        
        String [] policyFiles = new String[1];
        policyFiles[0] = policyFile;
        simplePDP = new SimplePDP_TEST(policyFiles);
        
        ResponseCtx response = simplePDP.evaluateInputStream(new ByteArrayInputStream(XACMLRequest.getBytes()));

        ByteArrayOutputStream os = new ByteArrayOutputStream();
        response.encode(os,new Indenter());
        String out = null;
        try {
            out = new String(os.toByteArray(), "UTF-8");
        } catch (Exception e) {
            System.err.print("Caught exception: " + e.getMessage());
        }
        System.out.println("TEST: \n" + out);
        
        return out;
    
    }
        
}
