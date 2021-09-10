
/*
 * @(#)StandardCombiningAlgFactory.java
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

package com.sun.xacml.combine;

import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import java.util.logging.Level;
import java.util.logging.Logger;


/**
 * This factory supports the standard set of algorithms specified in XACML
 * 1.0 and 1.1. It is the default factory used by the system, and imposes
 * a singleton pattern insuring that there is only ever one instance of
 * this class.
 * <p>
 * Note that because this supports only the standard algorithms, this
 * factory does not allow the addition of any other algorithms. If you call
 * <code>addAlgorithm</code> on an instance of this class, an exception
 * will be thrown. If you need a standard factory that is modifiable, you
 * should create a new <code>BaseCombiningAlgFactory</code> (or some other
 * <code>CombiningAlgFactory</code>) and configure it with the standard
 * algorithms using <code>getStandardAlgorithms</code> (or, in the case of
 * <code>BaseAttributeFactory</code>, by providing the datatypes in the
 * constructor).
 *
 * @since 1.2
 * @author Seth Proctor
 */
public class StandardCombiningAlgFactory extends BaseCombiningAlgFactory
{

    // the single factory instance
    private static StandardCombiningAlgFactory factoryInstance = null;

    // the algorithms supported by this factory
    private static Set supportedAlgorithms = null;

    // the logger we'll use for all messages
    private static final Logger logger =
        Logger.getLogger(StandardCombiningAlgFactory.class.getName());

    /**
     * Default constructor.
     */
    private StandardCombiningAlgFactory() {
        super(supportedAlgorithms);
    }

    /**
     * Private initializer for the supported algorithms. This isn't called
     * until something needs these values, and is only called once.
     */
    private static void initAlgorithms() {
        logger.config("Initializing standard combining algorithms");

        supportedAlgorithms = new HashSet();
        
        supportedAlgorithms.add(new DenyOverridesRuleAlg());
        supportedAlgorithms.add(new DenyOverridesPolicyAlg());
        
        supportedAlgorithms.add(new OrderedDenyOverridesRuleAlg());
        supportedAlgorithms.add(new OrderedDenyOverridesPolicyAlg());
        
        supportedAlgorithms.add(new PermitOverridesRuleAlg());
        supportedAlgorithms.add(new PermitOverridesPolicyAlg());
        
        supportedAlgorithms.add(new OrderedPermitOverridesRuleAlg());
        supportedAlgorithms.add(new OrderedPermitOverridesPolicyAlg());
        
        supportedAlgorithms.add(new FirstApplicableRuleAlg());
        supportedAlgorithms.add(new FirstApplicablePolicyAlg());
        
        supportedAlgorithms.add(new OnlyOneApplicablePolicyAlg());
    }

    /**
     * Returns an instance of this factory. This method enforces a singleton
     * model, meaning that this always returns the same instance, creating
     * the factory if it hasn't been requested before. This is the default
     * model used by the <code>CombiningAlgFactory</code>, ensuring quick
     * access to this factory.
     *
     * @return the factory instance
     */
    public static StandardCombiningAlgFactory getFactory() {
        if (factoryInstance == null) {
            synchronized (StandardCombiningAlgFactory.class) {
                if (factoryInstance == null) {
                    initAlgorithms();
                    factoryInstance = new StandardCombiningAlgFactory();
                }
            }
        }
        
        return factoryInstance;
    }

    /**
     * Returns the set of algorithms that this standard factory supports.
     *
     * @return a <code>Set</code> of <code>CombiningAlgorithm</code>s
     */
    public Set getStandardAlgorithms() {
        return Collections.unmodifiableSet(supportedAlgorithms);
    }

    /**
     * Throws an <code>UnsupportedOperationException</code> since you are not
     * allowed to modify what a standard factory supports.
     *
     * @param alg the combining algorithm to add
     *
     * @throws UnsupportedOperationException always
     */
    public void addAlgorithm(CombiningAlgorithm alg) {
        throw new UnsupportedOperationException("a standard factory cannot " +
                                                "support new algorithms");
    }

}
