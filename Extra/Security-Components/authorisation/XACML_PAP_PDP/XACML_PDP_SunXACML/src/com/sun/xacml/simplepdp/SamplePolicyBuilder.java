package com.sun.xacml.simplepdp;
/*
 * @(#)SamplePolicyBuilder.java
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


import com.sun.xacml.Indenter;
import com.sun.xacml.Policy;
import com.sun.xacml.Rule;
import com.sun.xacml.Target;
import com.sun.xacml.TargetMatch;
import com.sun.xacml.UnknownIdentifierException;

import com.sun.xacml.attr.AnyURIAttribute;
import com.sun.xacml.attr.AttributeDesignator;
import com.sun.xacml.attr.AttributeValue;
import com.sun.xacml.attr.StringAttribute;

import com.sun.xacml.combine.CombiningAlgFactory;
import com.sun.xacml.combine.OrderedPermitOverridesRuleAlg;
import com.sun.xacml.combine.RuleCombiningAlgorithm;

import com.sun.xacml.cond.Apply;
import com.sun.xacml.cond.Function;
import com.sun.xacml.cond.FunctionFactory;

import com.sun.xacml.ctx.Result;

import java.net.URI;
import java.net.URISyntaxException;

import java.util.ArrayList;
import java.util.List;


/**
 * This is an example program that shows how to build and generate an XACML
 * Policy. This doesn't show all the available features, but it provides a
 * good sample of commonly used functionality. Note that there's a fair amount
 * of duplicate code in this class, since verbosity (in this case) makes the
 * code a little easier to understand. An equivalent Polict to that generated
 * here is found in the policy directory as generated.xml. The generated
 * request can be used with this policy.
 *
 * @since 1.1
 * @author seth proctor
 */
public class SamplePolicyBuilder
{

    /**
     * Simple helper routine that creates a TargetMatch instance.
     *
     * @param type the type of match
     * @param functionId the matching function identifier
     * @param designator the AttributeDesignator used in this match
     * @param value the AttributeValue used in this match
     *
     * @return the matching element
     */
    public static TargetMatch createTargetMatch(int type, String functionId,
                                                AttributeDesignator designator,
                                                AttributeValue value) {
        try {
            // get the factory that handles Target functions and get an
            // instance of the right function
            FunctionFactory factory = FunctionFactory.getTargetInstance();
            Function function = factory.createFunction(functionId);
        
            // create the TargetMatch
            return new TargetMatch(type, function, designator, value);
        } catch (Exception e) {
            // note that in this example, we should never hit this case, but
            // in the real world you need to worry about exceptions, especially
            // from the factory
            return null;
        }
    }

    /**
     * Creates the Target used in the Policy. This Target specifies that
     * the Policy applies to any example.com users who are requesting some
     * form of access to server.example.com.
     *
     * @return the target
     *
     * @throws URISyntaxException if there is a problem with any of the URIs
     */
    public static Target createPolicyTarget() throws URISyntaxException {
        List subjects = new ArrayList();
        List resources = new ArrayList();

        // create the Subject section
        List subject = new ArrayList();
        
        String subjectMatchId =
            "urn:oasis:names:tc:xacml:1.0:function:rfc822Name-match";

        URI subjectDesignatorType =
            new URI("urn:oasis:names:tc:xacml:1.0:data-type:rfc822Name");
        URI subjectDesignatorId =
            new URI("urn:oasis:names:tc:xacml:1.0:subject:subject-id");
        AttributeDesignator subjectDesignator =
            new AttributeDesignator(AttributeDesignator.SUBJECT_TARGET,
                                    subjectDesignatorType,
                                    subjectDesignatorId, false);

        StringAttribute subjectValue =
            new StringAttribute("users.example.com");
        
        subject.add(createTargetMatch(TargetMatch.SUBJECT, subjectMatchId,
                                      subjectDesignator, subjectValue));

        // create the Resource section
        List resource = new ArrayList();

        String resourceMatchId =
            "urn:oasis:names:tc:xacml:1.0:function:anyURI-equal";

        URI resourceDesignatorType =
            new URI("http://www.w3.org/2001/XMLSchema#anyURI");
        URI resourceDesignatorId =
            new URI("urn:oasis:names:tc:xacml:1.0:resource:resource-id");
        AttributeDesignator resourceDesignator =
            new AttributeDesignator(AttributeDesignator.RESOURCE_TARGET,
                                    resourceDesignatorType,
                                    resourceDesignatorId, false);

        AnyURIAttribute resourceValue =
            new AnyURIAttribute(new URI("http://server.example.com/"));

        resource.add(createTargetMatch(TargetMatch.RESOURCE, resourceMatchId,
                                       resourceDesignator, resourceValue));

        // put the Subject and Resource sections into their lists
        subjects.add(subject);
        resources.add(resource);

        // create & return the new Target
        return new Target(subjects, resources, null);
    }

    /**
     * Creates the Target used in the Condition. This Target specifies that
     * the Condition applies to anyone taking the action commit.
     *
     * @return the target
     *
     * @throws URISyntaxException if there is a problem with any of the URIs
     */
    public static Target createRuleTarget() throws URISyntaxException {
        List actions = new ArrayList();
        
        // create the Action section
        List action = new ArrayList();

        String actionMatchId =
            "urn:oasis:names:tc:xacml:1.0:function:string-equal";

        URI actionDesignatorType =
            new URI("http://www.w3.org/2001/XMLSchema#string");
        URI actionDesignatorId =
            new URI("urn:oasis:names:tc:xacml:1.0:action:action-id");
        AttributeDesignator actionDesignator =
            new AttributeDesignator(AttributeDesignator.ACTION_TARGET,
                                    actionDesignatorType,
                                    actionDesignatorId, false);

        StringAttribute actionValue = new StringAttribute("commit");

        action.add(createTargetMatch(TargetMatch.ACTION, actionMatchId,
                                     actionDesignator, actionValue));

        // put the Action section in the Actions list
        actions.add(action);

        // create & return the new Target
        return new Target(null, null, actions);
    }

    /**
     * Creates the Condition used in the Rule. Note that a Condition is just a
     * special kind of Apply.
     *
     * @return the condition
     *
     * @throws URISyntaxException if there is a problem with any of the URIs
     */
    public static Apply createRuleCondition() throws URISyntaxException {
        List conditionArgs = new ArrayList();

        // get the function that the condition uses
        FunctionFactory factory = FunctionFactory.getConditionInstance();
        Function conditionFunction = null;
        try {
            conditionFunction =
                factory.createFunction("urn:oasis:names:tc:xacml:1.0:function:"
                                       + "string-equal");
        } catch (Exception e) {
            // see comment in createTargetMatch()
            return null;
        }
        
        // now create the apply section that gets the designator value
        List applyArgs = new ArrayList();

        factory = FunctionFactory.getGeneralInstance();
        Function applyFunction = null;
        try {
            applyFunction =
                factory.createFunction("urn:oasis:names:tc:xacml:1.0:function:"
                                       + "string-one-and-only");
        } catch (Exception e) {
            // see comment in createTargetMatch()
            return null;
        }
        
        URI designatorType =
            new URI("http://www.w3.org/2001/XMLSchema#string");
        URI designatorId =
            new URI("group");
        URI designatorIssuer =
            new URI("admin@users.example.com");
        AttributeDesignator designator =
            new AttributeDesignator(AttributeDesignator.SUBJECT_TARGET,
                                    designatorType, designatorId, false,
                                    designatorIssuer);
        applyArgs.add(designator);

        Apply apply = new Apply(applyFunction, applyArgs, false);
        
        // add the new apply element to the list of inputs to the condition
        conditionArgs.add(apply);

        // create an AttributeValue and add it to the input list
        StringAttribute value = new StringAttribute("developers");
        conditionArgs.add(value);

        // finally, create & return our Condition
        return new Apply(conditionFunction, conditionArgs, true);
    }

    /**
     * Creates the Rule used in the Policy.
     *
     * @return the rule
     *
     * @throws URISyntaxException if there is a problem with any of the URIs
     */
    public static Rule createRule() throws URISyntaxException {
        // define the identifier for the rule
        URI ruleId = new URI("CommitRule");

        // define the effect for the Rule
        int effect = Result.DECISION_PERMIT;

        // get the Target for the rule
        Target target = createRuleTarget();

        // get the Condition for the rule
        Apply condition = createRuleCondition();
        
        return new Rule(ruleId, effect, null, target, condition);
    }

    /**
     * Command-line routine that bundles together all the information needed
     * to create a Policy and then encodes the Policy, printing to standard
     * out.
     */
    public static void main(String [] args) throws Exception {
        // define the identifier for the policy
        URI policyId = new URI("GeneratedPolicy");

        // get the combining algorithm for the policy
        URI combiningAlgId = new URI(OrderedPermitOverridesRuleAlg.algId);
        CombiningAlgFactory factory = CombiningAlgFactory.getInstance();
        RuleCombiningAlgorithm combiningAlg =
            (RuleCombiningAlgorithm)(factory.createAlgorithm(combiningAlgId));

        // add a description for the policy
        String description =
            "This policy applies to any accounts at users.example.com " +
            "accessing server.example.com. The one Rule applies to the " +
            "specific action of doing a CVS commit, but other Rules could " +
            "be defined that handled other actions. In this case, only " +
            "certain groups of people are allowed to commit. There is a " +
            "final fall-through rule that always returns Deny.";

        // create the target for the policy
        Target policyTarget = createPolicyTarget();

        // create the commit rule
        Rule commitRule = createRule();

        // create the default, fall-through rule
        Rule defaultRule = new Rule(new URI("FinalRule"), Result.DECISION_DENY,
                                    null, null, null);

        // create a list for the rules and add our rules in order
        List ruleList = new ArrayList();
        ruleList.add(commitRule);
        ruleList.add(defaultRule);

        // create the policy
        Policy policy = new Policy(policyId, combiningAlg, description,
                                   policyTarget, ruleList);

        // finally, encode the policy and print it to standard out
        policy.encode(System.out, new Indenter());
    }
    
}
