package apptransformer;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;

import com.google.common.collect.Lists;

import soot.Value;
import soot.Body;
import soot.BodyTransformer;
import soot.G;
import soot.Local;
import soot.PackManager;
import soot.PatchingChain;
import soot.Scene;
import soot.SootMethod;
import soot.Transform;
import soot.Type;
import soot.Unit;
import soot.jimple.AbstractStmtSwitch;
import soot.jimple.InvokeExpr;
import soot.jimple.InvokeStmt;
import soot.jimple.Jimple;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.jimple.internal.AbstractInvokeExpr;
import soot.options.Options;

// Code is inspired by a tutorial on Soot's Github wiki on: https://github.com/Sable/soot/wiki/Instrumenting-Android-Apps-with-Soot

public class TransformAPKs_IntentSinks {
	
	// the current Intent ID
	static int numSendIntentMethods = 0;
	
	// Lets call all the fields for newField_X, so we can find them again!
	static String newField = "newField_";
	
	// We also might need the permission of the Intent method. Lets save it in this string, so we can search for this again.
	static String tempString = "INTENT_PERMISSION=";

	
	public static void main(String[] args) {
		
		// We need the phantom classes for this to work
		Options.v().set_allow_phantom_refs(true);
		
		//prefer Android APK files// -src-prec apk
		Options.v().set_src_prec(Options.src_prec_apk);

		//output as APK, too//-f J
		Options.v().set_output_format(Options.output_format_dex);

		// Lets add a transform to Soot. This way we add a new step in the Soot pipeline
		PackManager.v().getPack("jtp").add(new Transform("jtp.myInstrumenter", new BodyTransformer() {	
			@Override
			protected void internalTransform(final Body b, String phaseName, @SuppressWarnings("rawtypes") Map options) {
				
				final PatchingChain<Unit> units = b.getUnits();	

				//important to use snapshotIterator here (we don't know why, but if the man says it!)
				for(Iterator<Unit> iter = units.snapshotIterator(); iter.hasNext();) {
					// Lets get the next unit
					final Unit u = iter.next();

					// Lets go over all the statements in the Unit
					// The AbstractStmtSwitch treats all statements alike, so we get them all
					u.apply(new AbstractStmtSwitch() {
						public void caseInvokeStmt(InvokeStmt stmt) {
							
							InvokeExpr invokeExpr = stmt.getInvokeExpr();
					
							// Lets look and see, if this is a statement we care about
							Boolean isIntentSendingMethod = intentSinkMethod(stmt);
							
							if (isIntentSendingMethod == true){
								// Lets log that we found something!
								G.v().out.println("We found an Intent!");
								
								// We check if the method we found have any arguments.
								if(invokeExpr.getArgCount()>0){
									
									//Lets check if any of the args are android.content.Intent
									
									// We reverse the list, to make sure that the Intent argument is always last, and therefore inserted just before the Intent method call
									// We do admit this is a bit hackish, but it works!
									for(Iterator arguments = Lists.reverse(invokeExpr.getArgs()).iterator();arguments.hasNext();){
										// Lets get the current argument
										Value arg = (Value) arguments.next();
										// We also need the type of it.
										Type argType = arg.getType();
										
										// if the sinkmethod contains a "Permission", this will be hit
										if(argType.toString().contentEquals("java.lang.String") || argType.toString() == "null_type"){
											
											
											// the permission is NULL, we change it to an string instead
											if(argType.toString() == "null_type") {
												// This means that the permission is Null, which is legit
												arg = StringConstant.v(tempString + "null");
											}
											else {
												// Else, lets just save the actual permission with our easy to find string.
												arg = StringConstant.v(tempString + arg.toString()); 
											}

											// get the first parameter, which is the Intent that the argument should be added to
											Local tmpRef = (Local)invokeExpr.getArgs().get(0);
											
											// We retrieve the Intent.putExtra method.
											SootMethod toCall = Scene.v().getSootClass("android.content.Intent").getMethod("android.content.Intent putExtra(java.lang.String,java.lang.String)");   

											// We then create a new unit, with our permission string.
											Unit newUnit = Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(tmpRef, toCall.makeRef(),arg, arg));
											units.insertBefore(newUnit, u);
										}
										
										if(argType.toString().contentEquals("android.content.Intent")){
											// It looks like we found a method, that only takes an Intent
								
											// Lets increment the Intent ID, so we know they are unique for the app
											incNumIntents();
											
											// Lets make our easy to find ID string
											String tempString = newField.concat(Integer.toString(getNumIntents()));
									
											Local tmpRef = (Local)arg;
											
											// Again, we get the Intent.putExtra method
											SootMethod toCall = Scene.v().getSootClass("android.content.Intent").getMethod("android.content.Intent putExtra(java.lang.String,java.lang.String)");   

											Value val2 = StringConstant.v(tempString);
											Value val3 = StringConstant.v(tempString);
											// And insert a new Unit in the code
											units.insertBefore(Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(tmpRef, toCall.makeRef(),val2, val3)), u);
										} 
									}

								}
							}
						}
					});

					//check that we did not mess up the Jimple
					b.validate(); 
				}
			}
		}));

		soot.Main.main(args);
	}

	static int getNumIntents(){
		return numSendIntentMethods;
	}

	static void incNumIntents(){
		numSendIntentMethods++;
	}
	
	public static boolean intentSinkMethod(Stmt stmt) {
		
		// Down here, we check if the current method is one we care about.
		// We only check the method signature, but it might be that an app developer thought that he also wanted to make a method with one of these signatures, that we dont care about.
		// But it doesnt matter, as Flowdroid will only find flows from the correct Context, ContextWrapper or Activity.

		AbstractInvokeExpr ie = (AbstractInvokeExpr) stmt.getInvokeExpr();
		SootMethod meth = ie.getMethod();
		String methodSubSig = meth.getSubSignature();
		
		// We need to check the following methods:
		/*
		 * sendBroadcast(Intent intent)
		 * sendBroadcast(Intent intent, String receiverPermission)
		 * sendOrderedBroadcast(Intent intent, String receiverPermission)
		 * sendStickyBroadcast(Intent intent)
		 * 
		 * startActivity(Intent intent)
		 * startActivity(Intent intent, Bundle options)
		 * startActivityForResult
		 * 
		 * startService(Intent service
		 * bindService(Intent, ServiceConnection, int)
		
		*/
		
		ArrayList<String> methods = new ArrayList<String>();
		methods.add("startActivity(android.content.Intent");
		methods.add("startActivityForResult(android.content.Intent,int");
		methods.add("startActivity (android.content.Intent,android.os.Bundle");
		
		methods.add("startService(android.content.Intent");
		methods.add("bindService(android.content.Intent,android.content.ServiceConnection");
		
		methods.add("sendBroadcast(android.content.Intent");
		methods.add("sendBroadcast(android.content.Intent,java.lang.String");
		methods.add("sendOrderedBroadcast(android.content.Intent,java.lang.String");
		methods.add("sendStickyBroadcast(android.content.Intent");
		 
		Boolean isCorrectMethod = false;
		
		for (String method : methods) {
			if(methodSubSig.contains(method)) {
				isCorrectMethod = true;
			}
		}
		
		if(!isCorrectMethod) {
			return false;
		}
		
		return true;
	}
}



