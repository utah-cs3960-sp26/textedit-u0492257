## Git Flow Questions
1. The main or master branch is for fully working code that is production-ready, where commits correspond to production releases, and each merge is tagged with a version number. The develop branch serves as the integration branch for new features and will serve as the basis for building what goes in the next release. This separation allows for ongoing integration and stable production history with explicitly versioned software.

2. A feature branch branches from the develop branch; its purpose is to develop new functionality and merges into develop when ready. It is not for urgent matters and not based on production code. A hotfix branch is specifically for fixing a critical bug in main, so it branches off of main and merges back into main and develop when patched.

3. A release branch is for preparing a production release, and is for final fixes, documentation tweaks, and minor bug fixes. Once created, develop stops for that release, and new features must wait until the next cycle.

4. According to the article,  with continuous delivery, especially with web apps, release, hotfix, and seperate develop and main is not necessary, as no support for multiple production versions is needed. Only a main branch and short-lived feature branches are necessary.


## Quickcheck Questions
1. The incorrect property is: "reverse (xs ++ ys) == reverse xs ++ reverse ys". The issue is that reversing a concatanation reverses the order of the elements and the sublists, so the correct one must swap xs and xy.

2. QuickCheck generates random lists, and discards any that do not satisfy xs. As list length increases, the probability that a randomly generated list is ordered drops quickly, so most long lists are rejected, and most accepted lists are short, which skews the distribution toward shorter, trivial, cases.

3. For normal, unconditional properties, QuickCheck generates a test case, and repeatedly checks it 100 times. For conditional properties, QuickCheck generates a conditional tes case, where if the condition is false, the test case is discarded. If the condition is true, it counts as one valid test. This continues until 100 valid tests are found or 1000 test candidates have been tried.  
