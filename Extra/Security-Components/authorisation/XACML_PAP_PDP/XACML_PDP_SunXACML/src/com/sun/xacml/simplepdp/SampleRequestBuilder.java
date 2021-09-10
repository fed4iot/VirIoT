package com.sun.xacml.simplepdp;
/*
 * @(#)SampleRequestBuilder.java
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


import com.sun.xacml.EvaluationCtx;
import com.sun.xacml.Indenter;

import com.sun.xacml.attr.AnyURIAttribute;
import com.sun.xacml.attr.RFC822NameAttribute;
import com.sun.xacml.attr.StringAttribute;

import com.sun.xacml.ctx.Attribute;
import com.sun.xacml.ctx.RequestCtx;
import com.sun.xacml.ctx.Subject;

import java.net.URI;
import java.net.URISyntaxException;

import java.util.HashSet;
import java.util.Set;


/**
 * This is an example program that shows how to build and generate an XACML
 * Request. This is a major part of what a PEP does. An equivalent Request to
 * that generated here is found in the request directory as generated.xml.
 * The generated policy can be used with this request.
 *
 * @since 1.1
 * @author seth proctor
 */
public class SampleRequestBuilder
{

    /**
     * Sets up the Subject section of the request. This Request only has
     * one Subject section, and it uses the default category. To create a
     * Subject with a different category, you simply specify the category
     * when you construct the Subject object.
     *
     * @return a Set of Subject instances for inclusion in a Request
     *
     * @throws URISyntaxException if there is a problem with a URI
     */
    public static Set setupSubjects() throws URISyntaxException {
        HashSet attributes = new HashSet();

        // setup the id and value for the requesting subject
        URI subjectId =
            new URI("urn:oasis:names:tc:xacml:1.0:subject:subject-id");
        RFC822NameAttribute value =
            new RFC822NameAttribute("seth@users.example.com");

        // create the subject section with two attributes, the first with
        // the subject's identity...
        attributes.add(new Attribute(subjectId, null, null, value));
        // ...and the second with the subject's group membership
        attributes.add(new Attribute(new URI("group"),
                                     "admin@users.example.com", null,
                                     new StringAttribute("developers")));

        // bundle the attributes in a Subject with the default category
        HashSet subjects = new HashSet();
        subjects.add(new Subject(attributes));

        return subjects;
    }

    /**
     * Creates a Resource specifying the resource-id, a required attribute.
     *
     * @return a Set of Attributes for inclusion in a Request
     *
     * @throws URISyntaxException if there is a problem with a URI
     */
    public static Set setupResource() throws URISyntaxException {
        HashSet resource = new HashSet();

        // the resource being requested
        AnyURIAttribute value =
            new AnyURIAttribute(new URI("http://server.example.com/"));

        // create the resource using a standard, required identifier for
        // the resource being requested
        resource.add(new Attribute(new URI(EvaluationCtx.RESOURCE_ID),
                                   null, null, value));
        
        return resource;
    }

    /**
     * Creates an Action specifying the action-id, an optional attribute.
     *
     * @return a Set of Attributes for inclusion in a Request
     *
     * @throws URISyntaxException if there is a problem with a URI
     */
    public static Set setupAction() throws URISyntaxException {
        HashSet action = new HashSet();

        // this is a standard URI that can optionally be used to specify
        // the action being requested
        URI actionId =
            new URI("urn:oasis:names:tc:xacml:1.0:action:action-id");

        // create the action
        action.add(new Attribute(actionId, null, null,
                                 new StringAttribute("commit")));

        return action;
    }

    /**
     * Command-line interface that creates a new Request by invoking the
     * static methods in this class. The Request has no Environment section.
     */
    public static void main(String [] args) throws Exception {
        // create the new Request...note that the Environment must be specified
        // using a valid Set, even if that Set is empty
        RequestCtx request =
            new RequestCtx(setupSubjects(), setupResource(),
                           setupAction(), new HashSet());
        
        // encode the Request and print it to standard out
        request.encode(System.out, new Indenter());
    }

}
