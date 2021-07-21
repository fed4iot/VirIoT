
/*
 * @(#)FunctionFactory.java
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

package com.sun.xacml.cond;

import com.sun.xacml.ParsingException;
import com.sun.xacml.UnknownIdentifierException;

import java.net.URI;

import java.util.Set;

import org.w3c.dom.Node;


/**
 * Factory used to create all functions. There are three kinds of factories:
 * general, condition, and target. These provide functions that can be used
 * anywhere, only in a condition's root and only in a target (respectively).
 * <p>
 * Note that all functions, except for abstract functions, are singletons, so
 * any instance that is added to a factory will be the same one returned
 * from the create methods. This is done because most functions don't have
 * state, so there is no need to have more than one, or to spend the time
 * creating multiple instances that all do the same thing.
 *
 * @since 1.0
 * @author Marco Barreno
 * @author Seth Proctor
 */
public abstract class FunctionFactory
{

    // the proxies used to get the default factorys
    private static FunctionFactoryProxy defaultFactoryProxy;

    /**
     * static intialiazer that sets up the default factory proxies
     * NOTE: this will change when the right setup mechanism is in place
     */
    static {
        defaultFactoryProxy = new FunctionFactoryProxy() {
                public FunctionFactory getTargetFactory() {
                    return StandardFunctionFactory.getTargetFactory();
                }
                public FunctionFactory getConditionFactory() {
                    return StandardFunctionFactory.getConditionFactory();
                }
                public FunctionFactory getGeneralFactory() {
                    return StandardFunctionFactory.getGeneralFactory();
                }
            };
    };

    /**
     * Default constructor. Used only by subclasses.
     */
    protected FunctionFactory() {

    }

    /**
     * Returns the default FunctionFactory that will only provide those
     * functions that are usable in Target matching.
     *
     * @return a <code>FunctionFactory</code> for target functions
     */
    public static final FunctionFactory getTargetInstance() {
        return defaultFactoryProxy.getTargetFactory();
    }

    /**
     * Returns the default FuntionFactory that will only provide those
     * functions that are usable in the root of the Condition. These Functions
     * are a superset of the Target functions.
     *
     * @return a <code>FunctionFactory</code> for condition functions
     */
    public static final FunctionFactory getConditionInstance() {
        return defaultFactoryProxy.getConditionFactory();
    }

    /**
     * Returns the default FunctionFactory that provides access to all the
     * functions. These Functions are a superset of the Condition functions.
     *
     * @return a <code>FunctionFactory</code> for all functions
     */
    public static final FunctionFactory getGeneralInstance() {
        return defaultFactoryProxy.getGeneralFactory();
    }

    /**
     * Sets the default factory. Note that this is just a placeholder for
     * now, and will be replaced with a more useful mechanism soon.
     */
    public static final void setDefaultFactory(FunctionFactoryProxy proxy) {
        defaultFactoryProxy = proxy;
    }

    /**
     * Adds the function to the factory. Most functions have no state, so
     * the singleton model used here is typically desireable. The factory will
     * not enforce the requirement that a Target or Condition matching function
     * must be boolean.
     *
     * @param function the <code>Function</code> to add to the factory
     *
     * @throws IllegalArgumentException if the function's identifier is already
     *                                  used
     */
    public abstract void addFunction(Function function);

    /**
     * Adds the abstract function proxy to the factory. This is used for
     * those functions which have state, or change behavior (for instance
     * the standard map function, which changes its return type based on
     * how it is used). 
     *
     * @param proxy the <code>FunctionProxy</code> to add to the factory
     * @param identity the function's identifier
     *
     * @throws IllegalArgumentException if the function's identifier is already
     *                                  used
     */
    public abstract void addAbstractFunction(FunctionProxy proxy,
                                             URI identity);

    /**
     * Adds a target function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addFunction(Function)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param function the function to add
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addTargetFunction(Function function) {
        getTargetInstance().addFunction(function);
    }

    /**
     * Adds an abstract target function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addAbstractFunction(FunctionProxy,URI)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param proxy the function proxy to add
     * @param identity the name of the function
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addAbstractTargetFunction(FunctionProxy proxy,
                                                 URI identity) {
        getTargetInstance().addAbstractFunction(proxy, identity);
    }

    /**
     * Adds a condition function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addFunction(Function)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param function the function to add
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addConditionFunction(Function function) {
        getConditionInstance().addFunction(function);
    }
    
    /**
     * Adds an abstract condition function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addAbstractFunction(FunctionProxy,URI)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param proxy the function proxy to add
     * @param identity the name of the function
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addAbstractConditionFunction(FunctionProxy proxy,
                                                    URI identity) {
        getConditionInstance().addAbstractFunction(proxy, identity);
    }

    /**
     * Adds a general function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addFunction(Function)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param function the function to add
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addGeneralFunction(Function function) {
        getGeneralInstance().addFunction(function);
    }

    /**
     * Adds an abstract general function.
     *
     * @deprecated As of version 1.2, replaced by
     *        {@link #addAbstractFunction(FunctionProxy,URI)}.
     *             The new factory system requires you to get a factory
     *             instance and then call the non-static methods on that
     *             factory. The static versions of these methods have been
     *             left in for now, but are slower and will be removed in
     *             a future version.
     *
     * @param proxy the function proxy to add
     * @param identity the name of the function
     * 
     * @throws IllegalArgumentException if the name is already in use
     */
    public static void addAbstractGeneralFunction(FunctionProxy proxy,
                                                  URI identity) {
        getGeneralInstance().addAbstractFunction(proxy, identity);
    }

    /**
     * Returns the function identifiers supported by this factory.
     *
     * @return a <code>Set</code> of <code>String</code>s
     */
    public abstract Set getSupportedFunctions();

    /**
     * Tries to get an instance of the specified function.
     *
     * @param identity the name of the function
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to an
     *                               abstract function, and should therefore
     *                               be created through createAbstractFunction
     */
    public abstract Function createFunction(URI identity)
        throws UnknownIdentifierException, FunctionTypeException;

    /**
     * Tries to get an instance of the specified function.
     *
     * @param identity the name of the function
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to an
     *                               abstract function, and should therefore
     *                               be created through createAbstractFunction
     */
    public abstract Function createFunction(String identity)
        throws UnknownIdentifierException, FunctionTypeException;

    /**
     * Tries to get an instance of the specified abstract function.
     *
     * @param identity the name of the function
     * @param root the DOM root containing info used to create the function
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to a
     *                               concrete function, and should therefore
     *                               be created through createFunction
     * @throws ParsingException if the function can't be created with the
     *                          given inputs
     */
    public abstract Function createAbstractFunction(URI identity, Node root)
        throws UnknownIdentifierException, ParsingException,
               FunctionTypeException;

    /**
     * Tries to get an instance of the specified abstract function.
     *
     * @param identity the name of the function
     * @param root the DOM root containing info used to create the function
     * @param xpathVersion the version specified in the contianing policy, or
     *                     null if no version was specified
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to a
     *                               concrete function, and should therefore
     *                               be created through createFunction
     * @throws ParsingException if the function can't be created with the
     *                          given inputs
     */
    public abstract Function createAbstractFunction(URI identity, Node root,
                                                    String xpathVersion)
        throws UnknownIdentifierException, ParsingException,
               FunctionTypeException;

    /**
     * Tries to get an instance of the specified abstract function.
     *
     * @param identity the name of the function
     * @param root the DOM root containing info used to create the function
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to a
     *                               concrete function, and should therefore
     *                               be created through createFunction
     * @throws ParsingException if the function can't be created with the
     *                          given inputs
     */
    public abstract Function createAbstractFunction(String identity, Node root)
        throws UnknownIdentifierException, ParsingException,
               FunctionTypeException;

    /**
     * Tries to get an instance of the specified abstract function.
     *
     * @param identity the name of the function
     * @param root the DOM root containing info used to create the function
     * @param xpathVersion the version specified in the contianing policy, or
     *                     null if no version was specified
     *
     * @throws UnknownIdentifierException if the name isn't known
     * @throws FunctionTypeException if the name is known to map to a
     *                               concrete function, and should therefore
     *                               be created through createFunction
     * @throws ParsingException if the function can't be created with the
     *                          given inputs
     */
    public abstract Function createAbstractFunction(String identity, Node root,
                                                    String xpathVersion)
        throws UnknownIdentifierException, ParsingException,
               FunctionTypeException;

}
