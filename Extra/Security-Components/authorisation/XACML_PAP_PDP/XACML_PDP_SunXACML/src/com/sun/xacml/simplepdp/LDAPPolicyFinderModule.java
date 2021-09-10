package com.sun.xacml.simplepdp;
/*
 * @(#)LDAPPolicyFinderModule.java
 *
 * Copyright 2004 Sun Microsystems, Inc. All Rights Reserved.
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


import com.sun.xacml.AbstractPolicy;
import com.sun.xacml.EvaluationCtx;
import com.sun.xacml.ParsingException;
import com.sun.xacml.Policy;
import com.sun.xacml.PolicyReference;
import com.sun.xacml.PolicySet;

import com.sun.xacml.ctx.Status;

import com.sun.xacml.finder.PolicyFinder;
import com.sun.xacml.finder.PolicyFinderModule;
import com.sun.xacml.finder.PolicyFinderResult;

import java.net.URI;

import java.util.ArrayList;
import java.util.Hashtable;

import javax.naming.Context;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;

import javax.naming.directory.Attribute;
import javax.naming.directory.Attributes;
import javax.naming.directory.BasicAttributes;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import javax.naming.directory.SearchResult;

import org.w3c.dom.Node;


/**
 * This is a template for managing policies provided by LDAP. It handles
 * both policy retrieval based on request applicability, and based on
 * referencing. It is not usable as-is, but has most of the plumbing
 * fleshed out.
 * <p>
 * For more information about how these modules work, look at the project
 * javadocs, the programmer's guide, or the example PolicyFinderModule in
 * the source examples of the 1.1 release.
 *
 * @author seth proctor
 */
public class LDAPPolicyFinderModule extends PolicyFinderModule
{

    /**
     * A made-up namespace for all policies referenced using LDAP. You don't
     * have to do this, it's just here as an example. Any policy references
     * that start with this namespace get handled by this module.
     */
    public static final String REFERENCE_NAMESPACE = "urn:com:sun:xacml:ldap";
    
    /**
     * The standard value that JNDI uses to do LDAP lookups
     */
    public static final String jndiCtx = "com.sun.jndi.ldap.LdapCtxFactory";

    /**
     * This is the LDAP server and root that we're using
     */
    public static final String serverRoot = "ldap://example.com/o=test,c=us";

    // the finder that is using this module
    private PolicyFinder finder;

    // the root context used for LDAP queries
    private DirContext directory;

    /**
     * Basic constructor where you can initialize private module data.
     */
    public LDAPPolicyFinderModule() throws NamingException {
        Hashtable env = new Hashtable();
        env.put(Context.INITIAL_CONTEXT_FACTORY, jndiCtx);
        env.put(Context.PROVIDER_URL, serverRoot);
        directory = new InitialDirContext(env);
    }

    /**
     * Always return true.
     *
     * @return true
     */
    public boolean isRequestSupported() {
        return false;
    }

    /**
     * Always return true.
     *
     * @return true
     */
    public boolean isIdReferenceSupported() {
        return true;
    }

    /**
     * Called when the <code>PolicyFinder</code> initializes. This lets your
     * code keep track of the finder, which is especially useful if you have
     * to create policy sets.
     *
     * @param finder the <code>PolicyFinder</code> that's using this module
     */
    public void init(PolicyFinder finder) {
        this.finder = finder;

        // if you want to add any caching, this should probably invalidate
        // the cache
    }

    /**
     * Tries to find a matching policy based on some request.
     *
     * @param context representation of the request
     *
     * @return the result of looking for a matching policy
     */
    public PolicyFinderResult findPolicy(EvaluationCtx context) {
        // NOTE: EvaluationCtx won't currently tell you about all the
        // values it has cached, which I think is the right behavior for
        // a number of reasons...as a result, however, it can make this
        // somewhat hard to implement with also getting the original
        // Request. In a future version I'll fix this, but for now you
        // won't be able to really optimize this routine. Sorry.

        // see the comments in findPolicy(URI, int) for details about the
        // retrieval process (which is the same, just based on different
        // data)...note that it's ok to find more than one matching policy
        // here, since we'll use the context to (hopefully) get down to
        // only one matching policy
        Node root = null;

        // for each retrieved policy, load it into a DOM tree, and then...
        String rootNode = root.getNodeName();
        AbstractPolicy policy = null;

        try {
            if (rootNode.equals("Policy")) {
                policy = Policy.getInstance(root);
            } else if (rootNode.equals("PolicySet")) {
                policy = PolicySet.getInstance(root, finder);
            } else {
                // this is an error, and you may need to stop at this point
            }
        } catch (ParsingException pe) {
            // some error occured while loading the policy, so we need to
            // return the error for the PolicyFinder to handle the problem
            ArrayList code = new ArrayList();
            String message = "error parsing a possibly pplicable policy: " +
                pe.getMessage();

            code.add(Status.STATUS_SYNTAX_ERROR);

            return new PolicyFinderResult(new Status(code, message));
        }

        // you need to make sure that only of the policies you find actually
        // apply to the request, so for each policy check that it matches,
        // and that nothing else has matched yet. Look in FilePolicyModule
        // for an example of exactly how to do this in findPolicy().

        // assuming you found exactly one matching policy, return it. If any
        // error occurs, then stop and return the error. If you find no
        // matching policies, return an empty PolicyFinderResult.

        return new PolicyFinderResult(policy);
    }
    
    /**
     * Tries to find a referenced policy.
     *
     * @param idReference an identifier specifying some policy
     * @param type type of reference (policy or policySet) as identified by
     *             the fields in <code>PolicyReference</code>
     *
     * @return the result of looking for the referenced policy
     */
    public PolicyFinderResult findPolicy(URI idReference, int type) {
        // handle this only if the reference is in our namespace
        if (! idReference.toString().startsWith(REFERENCE_NAMESPACE))
            return new PolicyFinderResult();

        // if you are doing any kind of caching, you should check now for
        // a cached version of the policy
        
        // Here's the code that you need to write...basically, you need to
        // decide how the request gets mapped into your LDAP schema, and
        // based on this what kinds of queries you want to make. See the
        // sampleQuery() method for info on how to query the directory. In
        // the end you should return with the DOM root of a policy (see
        // the example module com.sun.xacml.finder.impl.FilePolicyModule
        // for how to get a DOM tree out of an XML document). If you
        // failed to find any matches, return an empty PolicyFinderResult.
        // If there was an error, return that error.

        // If you found more than one matching policy, this is an error.

        // if we're still here then the retrieval mechanism found an XML
        // document...you should replace this line to reference the retrieved
        // XML instance
        Node root = null;

        // this will be the policy that was referenced
        AbstractPolicy policy;

        try {
            if (type == PolicyReference.POLICY_REFERENCE) {
                // a policy is being referenced
                policy = Policy.getInstance(root);
            } else {
                // a policy set is being referenced
                policy = PolicySet.getInstance(root, finder);
            }
        } catch (ParsingException pe) {
            // some error occured while loading the policy, so we need to
            // return the error for the PolicyFinder to handle the problem
            ArrayList code = new ArrayList();
            String message = "error parsing referenced policy \"" +
                idReference.toString() + "\": " + pe.getMessage();

            code.add(Status.STATUS_SYNTAX_ERROR);

            return new PolicyFinderResult(new Status(code, message));
        }

        // if we got here then we loaded a new policy...we may want to cache
        // it or otherwise track it

        // now return the policy
        return new PolicyFinderResult(policy);
    }

    /**
     * This wouldn't be used directly by your code. It's just provided here
     * as an example of how you query LDAP in the Java Programming Language.
     * In this case, we're looking in ou=policies,o=test,c=us for any
     * entries under the attribute role that match the string manager. This
     * is a pretty basic example...
     */
    private void sampleQuery() throws Exception {
        Attributes attrs = new BasicAttributes("role", "manager", true);
        NamingEnumeration enum_ = directory.search("ou=policies", attrs);

        if (! enum_.hasMore()) {
            System.out.println("couldn't find any entries");
        } else {
            // you can now iterate through the entries
            SearchResult result = (SearchResult)(enum_.next());
        }
    }

}
